// src/components/AgentTimeline.jsx
import React, { useEffect, useState } from "react";
import { AGENT_TIMELINE_STEPS } from "../lib/demoData";

export default function AgentTimeline({ isRunning, completedSteps = [], currentStep = null }) {
  const [animated, setAnimated] = useState([]);

  useEffect(() => {
    if (!isRunning) {
      setAnimated(completedSteps);
      return;
    }
    // Animate steps appearing one by one
    let i = 0;
    const interval = setInterval(() => {
      setAnimated((prev) => {
        const next = AGENT_TIMELINE_STEPS[i]?.id;
        if (!next) { clearInterval(interval); return prev; }
        i++;
        return [...prev, next];
      });
    }, 600);
    return () => clearInterval(interval);
  }, [isRunning, completedSteps]);

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}>
        <span style={styles.pill}>AGENT TIMELINE</span>
        {isRunning && <span style={styles.liveDot} />}
      </div>
      <div style={styles.steps}>
        {AGENT_TIMELINE_STEPS.map((step, i) => {
          const done = animated.includes(step.id);
          const active = currentStep === step.id && !done;
          return (
            <div key={step.id} style={styles.stepRow}>
              {/* Connector line */}
              {i < AGENT_TIMELINE_STEPS.length - 1 && (
                <div
                  style={{
                    ...styles.connector,
                    background: done ? "rgba(0,229,160,0.5)" : "var(--border)",
                  }}
                />
              )}
              {/* Icon */}
              <div
                style={{
                  ...styles.icon,
                  background: done
                    ? "rgba(0,229,160,0.15)"
                    : active
                    ? "rgba(245,166,35,0.15)"
                    : "var(--panel-strong)",
                  border: done
                    ? "1.5px solid rgba(0,229,160,0.5)"
                    : active
                    ? "1.5px solid rgba(245,166,35,0.5)"
                    : "1.5px solid var(--border-strong)",
                }}
              >
                {done ? (
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                    <path d="M2 5.5L4.5 8L9 3" stroke="#00e5a0" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : active ? (
                  <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#f5a623", display: "inline-block", animation: "pulse 1s infinite" }} />
                ) : (
                  <span style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--border-strong)", display: "inline-block" }} />
                )}
              </div>
              {/* Label */}
              <div style={styles.stepText}>
                <div
                  style={{
                    ...styles.stepLabel,
                    color: done ? "var(--text)" : active ? "#f5a623" : "var(--muted-soft)",
                  }}
                >
                  {step.label}
                </div>
                {done && (
                  <div style={styles.stepDetail}>{step.detail}</div>
                )}
              </div>
            </div>
          );
        })}
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
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "18px",
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "var(--muted)",
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#f5a623",
    boxShadow: "0 0 8px #f5a623",
    animation: "pulse 1s infinite",
  },
  steps: {
    display: "flex",
    flexDirection: "column",
    gap: "0",
  },
  stepRow: {
    display: "flex",
    alignItems: "flex-start",
    gap: "12px",
    position: "relative",
    paddingBottom: "14px",
  },
  connector: {
    position: "absolute",
    left: "15px",
    top: "28px",
    width: "1.5px",
    height: "calc(100% - 14px)",
    transition: "background 0.4s ease",
  },
  icon: {
    width: 30,
    height: 30,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    transition: "all 0.3s ease",
    zIndex: 1,
  },
  stepText: {
    paddingTop: "5px",
  },
  stepLabel: {
    fontFamily: "'Inter', sans-serif",
    fontSize: "13px",
    fontWeight: 500,
    transition: "color 0.3s ease",
  },
  stepDetail: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    color: "var(--muted-soft)",
    marginTop: "2px",
  },
};
