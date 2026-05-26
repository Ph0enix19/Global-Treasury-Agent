// src/components/DiscrepancyPanel.jsx
import React from "react";

export default function DiscrepancyPanel({ result }) {
  if (!result || result.status === "matched") return null;

  const { warnings = [], explanation, fee_trace, best_match, status } = result;

  const expectedNet = fee_trace?.expected_credit ?? fee_trace?.net_after_fee;
  const received = best_match?.credit_amount;
  const gap = expectedNet && received ? Math.abs(expectedNet - received).toFixed(2) : null;

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.title}>
          {status === "needs_review" ? "⚠ Needs Review" : "✗ Unmatched"}
        </span>
        <span style={styles.pill}>DISCREPANCY PANEL</span>
      </div>

      {gap && (
        <div style={styles.gapBox}>
          <div style={styles.gapLabel}>Amount Discrepancy</div>
          <div style={styles.gapValue}>
            {fee_trace?.currency} {gap}
          </div>
          <div style={styles.gapNote}>
            Expected {fee_trace?.currency} {expectedNet?.toFixed(2)} — Received {best_match?.currency} {received?.toFixed(2)}
          </div>
        </div>
      )}

      <div style={styles.explanationBox}>
        <div style={styles.explanationLabel}>AI Explanation (Chutes)</div>
        <p style={styles.explanationText}>{explanation}</p>
      </div>

      {warnings.length > 0 && (
        <div style={styles.warningList}>
          <div style={styles.warningTitle}>Flags Raised</div>
          {warnings.map((w, i) => (
            <div key={i} style={styles.warningItem}>
              <span style={styles.warningIcon}>▲</span>
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      <div style={styles.action}>
        <div style={styles.actionText}>Action Required</div>
        <div style={styles.actionDesc}>
          A finance team member should verify this transaction before posting it to the ledger.
          Check with the bank whether an intermediary charge was applied.
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "rgba(245,166,35,0.04)",
    border: "1px solid rgba(245,166,35,0.2)",
    borderRadius: "12px",
    padding: "20px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
  },
  title: {
    fontFamily: "'Syne', sans-serif",
    fontSize: "15px",
    fontWeight: 700,
    color: "#f5a623",
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "rgba(245,166,35,0.6)",
  },
  gapBox: {
    background: "rgba(245,166,35,0.08)",
    borderRadius: "10px",
    padding: "14px 16px",
    marginBottom: "16px",
    textAlign: "center",
  },
  gapLabel: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    color: "rgba(245,166,35,0.7)",
    marginBottom: "4px",
    letterSpacing: "0.06em",
  },
  gapValue: {
    fontFamily: "'Syne', sans-serif",
    fontSize: "28px",
    fontWeight: 800,
    color: "#f5a623",
    marginBottom: "4px",
  },
  gapNote: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    color: "rgba(245,166,35,0.5)",
  },
  explanationBox: {
    background: "var(--panel)",
    borderRadius: "8px",
    padding: "14px",
    marginBottom: "14px",
  },
  explanationLabel: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-soft)",
    marginBottom: "8px",
    letterSpacing: "0.06em",
  },
  explanationText: {
    fontFamily: "'Inter', sans-serif",
    fontSize: "13px",
    lineHeight: "1.65",
    color: "var(--text-soft)",
    margin: 0,
  },
  warningList: {
    marginBottom: "14px",
  },
  warningTitle: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-soft)",
    marginBottom: "8px",
    letterSpacing: "0.06em",
  },
  warningItem: {
    display: "flex",
    gap: "8px",
    alignItems: "flex-start",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "12px",
    color: "#f5a623",
    marginBottom: "6px",
  },
  warningIcon: {
    fontSize: "10px",
    flexShrink: 0,
    paddingTop: "2px",
  },
  action: {
    background: "var(--panel)",
    borderRadius: "8px",
    padding: "12px 14px",
  },
  actionText: {
    fontFamily: "'Syne', sans-serif",
    fontSize: "12px",
    fontWeight: 700,
    color: "var(--text)",
    marginBottom: "4px",
  },
  actionDesc: {
    fontFamily: "'Inter', sans-serif",
    fontSize: "12px",
    color: "var(--muted)",
    lineHeight: "1.5",
  },
};
