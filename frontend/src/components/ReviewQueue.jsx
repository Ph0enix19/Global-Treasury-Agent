// src/components/ReviewQueue.jsx
import React from "react";
import ConfidenceBadge from "./ConfidenceBadge";

export default function ReviewQueue({ cases = [], activeId, onSelect }) {
  const pending = cases.filter((c) => c.status !== "matched");

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.pill}>REVIEW QUEUE</span>
        <span
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "11px",
            color: pending.length > 0 ? "#f5a623" : "#00e5a0",
            fontWeight: 600,
          }}
        >
          {pending.length} exception{pending.length !== 1 ? "s" : ""}
        </span>
      </div>

      {pending.length === 0 ? (
        <div style={styles.empty}>
          <span style={{ fontSize: "20px" }}>✓</span>
          <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "#00e5a0", marginTop: "6px" }}>
            All transactions reconciled
          </div>
        </div>
      ) : (
        <div style={styles.list}>
          {pending.map((c) => (
            <div
              key={c.job_id}
              onClick={() => onSelect && onSelect(c.job_id)}
              style={{
                ...styles.item,
                background: activeId === c.job_id ? "rgba(245,166,35,0.08)" : "var(--panel-soft)",
                border: activeId === c.job_id ? "1px solid rgba(245,166,35,0.3)" : "1px solid var(--border-soft)",
                cursor: "pointer",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "13px", fontWeight: 600, color: "var(--text)", minWidth: 0, overflowWrap: "anywhere" }}>
                  {c.invoice?.invoice_number || c.job_id}
                </span>
                <ConfidenceBadge status={c.status} confidence={c.confidence} />
              </div>
              <div style={{ fontFamily: "'Inter', sans-serif", fontSize: "12px", color: "var(--muted)", lineHeight: "1.4" }}>
                {c.explanation?.slice(0, 100)}…
              </div>
              <div style={{ marginTop: "8px", display: "flex", gap: "12px" }}>
                <span style={styles.meta}>{c.invoice?.currency} {c.invoice?.amount?.toFixed(2)}</span>
                <span style={styles.meta}>{c.invoice?.date}</span>
              </div>
            </div>
          ))}
        </div>
      )}
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
  empty: {
    textAlign: "center",
    padding: "24px 0",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  item: {
    borderRadius: "8px",
    padding: "14px",
    transition: "all 0.2s ease",
  },
  meta: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    color: "var(--muted-soft)",
  },
};
