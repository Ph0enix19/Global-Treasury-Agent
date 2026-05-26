// src/lib/api.js
// API wrapper. Demo cases can fall back to mock data; real uploads must not.

import { DEMO_CASES } from "./demoData";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 15000;
const UPLOAD_TIMEOUT_MS = 120000;
const RECONCILE_TIMEOUT_MS = 120000;
const ARTIFACT_TIMEOUT_MS = 30000;

async function errorFromResponse(res, fallback) {
  try {
    const payload = await res.json();
    return payload.detail || fallback;
  } catch {
    return fallback;
  }
}

async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS, label = "Request") {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    return res;
  } catch (err) {
    clearTimeout(id);
    if (err?.name === "AbortError") {
      throw new Error(`${label} timed out after ${Math.round(timeoutMs / 1000)} seconds.`);
    }
    throw err;
  }
}

// GET /api/health
export async function checkHealth() {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

// GET /api/demo?case=<caseName>
// caseName: "matched" | "needs_review" | "unmatched" (more cases coming from Tawila's PR)
// Falls back to local mock if backend is unreachable.
export async function getDemoCase(caseName = "matched") {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/api/demo?case=${caseName}`);
    if (res.ok) return await res.json();
  } catch {
    // fall through to mock
  }
  // Fallback: find matching case from local mock data
  const fallback =
    DEMO_CASES.find((c) => c.status === caseName) ||
    DEMO_CASES.find((c) => c.job_id === caseName) ||
    DEMO_CASES[0];
  return { ...fallback, source: "mock" };
}

// POST /api/upload — upload invoice, payment proof, bank statement
export async function uploadFiles({ invoice, paymentProof, bankStatement }) {
  if (!invoice || !paymentProof || !bankStatement) {
    throw new Error("Upload requires an invoice, payment proof, and bank statement.");
  }

  const form = new FormData();
  form.append("invoice", invoice);
  form.append("payment_proof", paymentProof);
  form.append("bank_statement", bankStatement);

  const res = await fetchWithTimeout(
    `${BASE_URL}/api/upload`,
    {
      method: "POST",
      body: form,
    },
    UPLOAD_TIMEOUT_MS,
    "Document upload"
  );
  if (!res.ok) {
    throw new Error(await errorFromResponse(res, "Upload failed."));
  }
  return await res.json();
}

// POST /api/reconcile — trigger full reconciliation pipeline
export async function reconcile(jobId) {
  const res = await fetchWithTimeout(
    `${BASE_URL}/api/reconcile`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: jobId }),
    },
    RECONCILE_TIMEOUT_MS,
    "Reconciliation"
  );
  if (!res.ok) {
    throw new Error(await errorFromResponse(res, "Reconciliation failed."));
  }
  return await res.json();
}

// GET /api/results/{job_id}
export async function getResults(jobId) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/api/results/${jobId}`);
    if (res.ok) return await res.json();
  } catch {
    // fall through
  }
  const found = DEMO_CASES.find((c) => c.job_id === jobId);
  return found || DEMO_CASES[0];
}

// GET /api/report/{job_id}
export async function getReportUrl(jobId) {
  return `${BASE_URL}/api/report/${jobId}`;
}

// GET /api/export/{job_id}
export async function getExportUrl(jobId) {
  return `${BASE_URL}/api/export/${jobId}`;
}

export async function fetchArtifact(url, filename) {
  const res = await fetchWithTimeout(url, {}, ARTIFACT_TIMEOUT_MS, "Audit artifact download");
  if (!res.ok) {
    throw new Error(await errorFromResponse(res, "Audit artifact is not available for this job."));
  }
  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.target = "_blank";
  if (filename) {
    link.download = filename;
  }
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}
