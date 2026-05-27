// src/components/DiscrepancyPanel.jsx
import React from "react";

export default function DiscrepancyPanel({ result }) {
  if (!result || result.status === "matched") return null;

  const { warnings = [], explanation, fee_trace, best_match, status, action_pack } = result;

  const expectedNet = fee_trace?.expected_credit ?? fee_trace?.net_after_fee;
  const received = best_match?.credit_amount;
  const gap =
    expectedNet != null && received != null
      ? Math.abs(expectedNet - received).toFixed(2)
      : null;
  const title = status === "needs_review" ? "Needs Review" : "Unmatched";

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.title}>{title}</span>
        <span style={styles.pill}>AGENTIC DISCREPANCY WORKFLOW</span>
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

      {action_pack && (
        <div style={styles.pack}>
          <div style={styles.packHeader}>
            <div>
              <div style={styles.packEyebrow}>ACTION PACK</div>
              <div style={styles.packCategory}>{action_pack.category?.replaceAll("_", " ")}</div>
            </div>
            <span style={styles.workflowBadge}>READY FOR FINANCE</span>
          </div>

          <div style={styles.workflowGrid}>
            <div style={styles.workflowItem}>
              <div style={styles.workflowLabel}>Likely Reason</div>
              <div style={styles.workflowText}>{action_pack.likely_reason}</div>
            </div>
            <div style={styles.workflowItem}>
              <div style={styles.workflowLabel}>Recommended Next Action</div>
              <div style={styles.workflowText}>{action_pack.recommended_next_action}</div>
            </div>
          </div>

          {action_pack.missing_evidence_checklist?.length > 0 && (
            <div style={styles.checklist}>
              <div style={styles.workflowLabel}>Missing Evidence Checklist</div>
              {action_pack.missing_evidence_checklist.map((item, index) => (
                <div key={index} style={styles.checklistItem}>
                  <span style={styles.checkMark}>□</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          )}

          <div style={styles.notificationBox}>
            <div style={styles.workflowLabel}>Mock Finance Notification</div>
            <div style={styles.notificationText}>{action_pack.mock_notification_message}</div>
          </div>

          <div style={styles.auditBox}>
            <div style={styles.workflowLabel}>Audit-Safe Explanation</div>
            <div style={styles.workflowText}>{action_pack.audit_safe_explanation}</div>
          </div>
        </div>
      )}

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
          {action_pack?.recommended_next_action ||
            "A finance team member should verify this transaction before posting it to the ledger."}
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
  pack: {
    background: "var(--panel)",
    border: "1px solid rgba(245,166,35,0.18)",
    borderRadius: "10px",
    padding: "14px",
    marginBottom: "14px",
  },
  packHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: "12px",
    alignItems: "flex-start",
    marginBottom: "12px",
    flexWrap: "wrap",
  },
  packEyebrow: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-soft)",
    letterSpacing: "0.08em",
    marginBottom: "4px",
  },
  packCategory: {
    fontFamily: "'Syne', sans-serif",
    fontSize: "15px",
    fontWeight: 800,
    color: "#f5a623",
    textTransform: "capitalize",
  },
  workflowBadge: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 700,
    letterSpacing: "0.06em",
    color: "#00e5a0",
    border: "1px solid rgba(0,229,160,0.22)",
    borderRadius: "999px",
    padding: "4px 9px",
    background: "rgba(0,229,160,0.05)",
    whiteSpace: "nowrap",
  },
  workflowGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(min(220px, 100%), 1fr))",
    gap: "10px",
    marginBottom: "12px",
  },
  workflowItem: {
    background: "var(--panel-soft)",
    border: "1px solid var(--border-soft)",
    borderRadius: "8px",
    padding: "12px",
    minWidth: 0,
  },
  workflowLabel: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-soft)",
    marginBottom: "7px",
    letterSpacing: "0.06em",
  },
  workflowText: {
    fontFamily: "'Inter', sans-serif",
    fontSize: "12px",
    color: "var(--text-soft)",
    lineHeight: "1.55",
  },
  checklist: {
    background: "var(--panel-soft)",
    border: "1px solid var(--border-soft)",
    borderRadius: "8px",
    padding: "12px",
    marginBottom: "12px",
  },
  checklistItem: {
    display: "flex",
    gap: "8px",
    alignItems: "flex-start",
    fontFamily: "'Inter', sans-serif",
    fontSize: "12px",
    color: "var(--text-soft)",
    lineHeight: "1.45",
    marginBottom: "6px",
  },
  checkMark: {
    fontFamily: "'IBM Plex Mono', monospace",
    color: "#f5a623",
    flexShrink: 0,
  },
  notificationBox: {
    background: "rgba(96,165,250,0.06)",
    border: "1px solid rgba(96,165,250,0.16)",
    borderRadius: "8px",
    padding: "12px",
    marginBottom: "12px",
  },
  notificationText: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    lineHeight: "1.55",
    color: "var(--text-soft)",
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
  },
  auditBox: {
    background: "rgba(0,229,160,0.04)",
    border: "1px solid rgba(0,229,160,0.12)",
    borderRadius: "8px",
    padding: "12px",
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
