// src/components/MatchCandidatesTable.jsx
import React from "react";

export default function MatchCandidatesTable({ rows = [], bestMatchId }) {
  if (!rows.length) return null;

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.pill}>MATCH CANDIDATES</span>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "var(--muted-faint)" }}>
          {rows.length} bank row{rows.length !== 1 ? "s" : ""} evaluated
        </span>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={styles.table}>
          <thead>
            <tr>
              {["Row ID", "Date", "Description", "Credit (MYR)", "Score", ""].map((h) => (
                <th key={h} style={styles.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const isBest = row.row_id === bestMatchId || row.is_best;
              return (
                <tr
                  key={row.row_id}
                  style={{
                    background: isBest ? "rgba(0,229,160,0.06)" : "transparent",
                    borderLeft: isBest ? "3px solid rgba(0,229,160,0.5)" : "3px solid transparent",
                    transition: "background 0.2s",
                  }}
                >
                  <td style={styles.td}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: "var(--muted-strong)" }}>
                      {row.row_id}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "var(--text)" }}>
                      {row.date}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "12px", color: "var(--text-soft)" }}>
                      {row.description}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "right" }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>
                      {row.credit_amount?.toFixed(2)}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    {row.match_score !== undefined ? (
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", justifyContent: "center" }}>
                        <div style={{ width: "40px", height: "4px", borderRadius: "2px", background: "var(--border)", overflow: "hidden" }}>
                          <div style={{ width: `${Math.round(row.match_score * 100)}%`, height: "100%", background: isBest ? "#00e5a0" : "var(--muted-faint)", borderRadius: "2px" }} />
                        </div>
                        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: isBest ? "#00e5a0" : "var(--muted-soft)" }}>
                          {Math.round(row.match_score * 100)}%
                        </span>
                      </div>
                    ) : "—"}
                  </td>
                  <td style={styles.td}>
                    {isBest && (
                      <span style={{
                        padding: "2px 8px",
                        borderRadius: "999px",
                        background: "rgba(0,229,160,0.12)",
                        border: "1px solid rgba(0,229,160,0.3)",
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: "10px",
                        color: "#00e5a0",
                        fontWeight: 600,
                        whiteSpace: "nowrap",
                      }}>
                        BEST MATCH
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "16px",
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "var(--muted)",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.08em",
    color: "var(--muted-faint)",
    textAlign: "left",
    padding: "6px 10px",
    borderBottom: "1px solid var(--border)",
  },
  td: {
    padding: "10px 10px",
    borderBottom: "1px solid var(--border-soft)",
    verticalAlign: "middle",
  },
};
