// src/components/FxFeeTraceCards.jsx
import React from "react";

function TraceRow({ label, value, highlight }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", padding: "7px 0", borderBottom: "1px solid var(--border-soft)" }}>
      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: "var(--muted)" }}>{label}</span>
      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", fontWeight: 600, color: highlight || "var(--text)", textAlign: "right", overflowWrap: "anywhere" }}>{value}</span>
    </div>
  );
}

export default function FxFeeTraceCards({ fxTrace, feeTrace }) {
  const percentageRate = feeTrace?.percentage_rate ?? (feeTrace?.percentage_fee ? feeTrace.percentage_fee / 100 : 0);
  const totalFee = feeTrace?.total_fee ?? feeTrace?.fee_amount;
  const expectedCredit = feeTrace?.expected_credit ?? feeTrace?.net_after_fee;

  return (
    <div className="trace-grid" style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "12px" }}>
      {/* FX Rate Card */}
      <div style={styles.card}>
        <div style={styles.cardTitle}>
          <span style={styles.pill}>FX RATE TRACE</span>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "var(--muted-faint)" }}>Frankfurter API</span>
        </div>
        {fxTrace ? (
          <>
            <TraceRow label="Base Currency" value={fxTrace.base_currency} />
            <TraceRow label="Target Currency" value={fxTrace.target_currency} />
            <TraceRow label="Exchange Rate" value={fxTrace.rate?.toFixed(4)} highlight="#a78bfa" />
            <TraceRow label="Rate Date" value={fxTrace.rate_date} />
            <TraceRow label="Converted Amount" value={`${fxTrace.target_currency} ${fxTrace.converted_amount?.toFixed(2)}`} highlight="#a78bfa" />
          </>
        ) : (
          <div style={styles.empty}>No FX data yet</div>
        )}
      </div>

      {/* Fee Rule Card */}
      <div style={styles.card}>
        <div style={styles.cardTitle}>
          <span style={styles.pill}>FEE RULE TRACE</span>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "var(--muted-faint)" }}>Deterministic</span>
        </div>
        {feeTrace ? (
          <>
            <TraceRow label="Rule Applied" value={feeTrace.rule_name} />
            <TraceRow label="% Fee" value={`${(percentageRate * 100).toFixed(1)}%`} />
            <TraceRow label="Flat Fee" value={feeTrace.flat_fee ? `${feeTrace.currency} ${feeTrace.flat_fee.toFixed(2)}` : "—"} />
            <TraceRow label="Fee Amount" value={`${feeTrace.currency} ${totalFee?.toFixed(2)}`} highlight="#f87171" />
            <TraceRow label="Net After Fee" value={`${feeTrace.currency} ${expectedCredit?.toFixed(2)}`} highlight="#00e5a0" />
          </>
        ) : (
          <div style={styles.empty}>No fee data yet</div>
        )}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: "12px",
    padding: "16px",
    boxShadow: "var(--shadow)",
    minWidth: 0,
  },
  cardTitle: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "12px",
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "var(--muted)",
  },
  empty: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "12px",
    color: "var(--muted-faint)",
    textAlign: "center",
    padding: "20px 0",
  },
};
