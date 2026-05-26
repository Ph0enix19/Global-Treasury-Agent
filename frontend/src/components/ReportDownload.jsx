// src/components/ReportDownload.jsx
import React, { useState } from "react";
import { fetchArtifact, getReportUrl, getExportUrl } from "../lib/api";

export default function ReportDownload({ jobId, disabled }) {
  const [pdfLoading, setPdfLoading] = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);

  const handlePdf = async () => {
    if (!jobId || disabled) return;
    setPdfLoading(true);
    try {
      const url = await getReportUrl(jobId);
      await fetchArtifact(url, `${jobId}_reconciliation_report.pdf`);
    } catch (e) {
      alert(e.message || "PDF report is not available for this job.");
    }
    setTimeout(() => setPdfLoading(false), 1000);
  };

  const handleCsv = async () => {
    if (!jobId || disabled) return;
    setCsvLoading(true);
    try {
      const url = await getExportUrl(jobId);
      await fetchArtifact(url, `${jobId}_audit_log.csv`);
    } catch (e) {
      alert(e.message || "CSV audit log is not available for this job.");
    }
    setTimeout(() => setCsvLoading(false), 1000);
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.pill}>AUDIT ARTIFACTS</span>
        <span
          title={jobId || "No job selected"}
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "10px",
            color: "var(--muted-faint)",
            maxWidth: 150,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            display: "block",
          }}
        >
          {jobId || "No job selected"}
        </span>
      </div>

      <div style={styles.buttons}>
        <button
          onClick={handlePdf}
          disabled={!jobId || disabled || pdfLoading}
          style={{ ...styles.btn, ...styles.btnPdf, opacity: (!jobId || disabled) ? 0.4 : 1 }}
        >
          <span style={styles.btnIcon}>📄</span>
          <div>
            <div style={styles.btnLabel}>{pdfLoading ? "Opening…" : "Reconciliation Report"}</div>
            <div style={styles.btnSub}>PDF with full audit trail</div>
          </div>
        </button>

        <button
          onClick={handleCsv}
          disabled={!jobId || disabled || csvLoading}
          style={{ ...styles.btn, ...styles.btnCsv, opacity: (!jobId || disabled) ? 0.4 : 1 }}
        >
          <span style={styles.btnIcon}>📊</span>
          <div>
            <div style={styles.btnLabel}>{csvLoading ? "Preparing…" : "CSV Audit Log"}</div>
            <div style={styles.btnSub}>Structured transaction export</div>
          </div>
        </button>
      </div>

      <div style={styles.note}>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "var(--muted-faint)" }}>
          ✦ Reports include FX trace, fee trace, match score, confidence, and explanation
        </span>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "var(--shadow)",
    minWidth: 0,
    overflow: "hidden",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "var(--muted)",
  },
  buttons: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
  },
  btn: {
    flex: 1,
    minWidth: "160px",
    minHeight: "74px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "14px 16px",
    borderRadius: "10px",
    border: "none",
    cursor: "pointer",
    transition: "all 0.2s ease",
    textAlign: "left",
  },
  btnPdf: {
    background: "rgba(167,139,250,0.1)",
    border: "1px solid rgba(167,139,250,0.25)",
  },
  btnCsv: {
    background: "rgba(0,229,160,0.08)",
    border: "1px solid rgba(0,229,160,0.2)",
  },
  btnIcon: {
    fontSize: "20px",
    flexShrink: 0,
  },
  btnLabel: {
    fontFamily: "'Syne', sans-serif",
    fontSize: "13px",
    fontWeight: 600,
    color: "var(--text)",
    marginBottom: "2px",
  },
  btnSub: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-soft)",
  },
  note: {
    marginTop: "14px",
    textAlign: "center",
  },
};
