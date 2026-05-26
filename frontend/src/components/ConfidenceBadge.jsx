// src/components/ConfidenceBadge.jsx
import React from "react";

export default function ConfidenceBadge({ status, confidence }) {
  const pct = Math.round((confidence || 0) * 100);

  const config = {
    matched: {
      label: "Matched",
      color: "#00e5a0",
      bg: "rgba(0,229,160,0.12)",
      border: "rgba(0,229,160,0.35)",
      dot: "#00e5a0",
    },
    needs_review: {
      label: "Needs Review",
      color: "#f5a623",
      bg: "rgba(245,166,35,0.12)",
      border: "rgba(245,166,35,0.35)",
      dot: "#f5a623",
    },
    unmatched: {
      label: "Unmatched",
      color: "#ff4d6d",
      bg: "rgba(255,77,109,0.12)",
      border: "rgba(255,77,109,0.35)",
      dot: "#ff4d6d",
    },
  };

  const c = config[status] || config.unmatched;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
      {/* Status pill */}
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "7px",
          padding: "5px 14px",
          borderRadius: "999px",
          background: c.bg,
          border: `1px solid ${c.border}`,
          color: c.color,
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
        }}
      >
        <span
          style={{
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            background: c.dot,
            boxShadow: `0 0 6px ${c.dot}`,
            display: "inline-block",
          }}
        />
        {c.label}
      </span>

      {/* Confidence meter */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div
          style={{
            width: "80px",
            height: "6px",
            borderRadius: "3px",
            background: "var(--border)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${pct}%`,
              height: "100%",
              background: c.color,
              borderRadius: "3px",
              transition: "width 1s ease",
            }}
          />
        </div>
        <span
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "13px",
            fontWeight: 600,
            color: c.color,
          }}
        >
          {pct}%
        </span>
        <span
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "11px",
            color: "var(--muted)",
            letterSpacing: "0.04em",
          }}
        >
          confidence
        </span>
      </div>
    </div>
  );
}
