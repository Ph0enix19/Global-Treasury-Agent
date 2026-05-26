// src/components/FileUpload.jsx
import React, { useRef, useState } from "react";

function UploadCard({ label, icon, accept, file, onFile, hint }) {
  const ref = useRef();
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  return (
    <div
      onClick={() => ref.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      style={{
        border: file
          ? "1.5px solid rgba(0,229,160,0.4)"
          : dragging
          ? "1.5px dashed var(--border-strong)"
          : "1.5px dashed var(--border)",
        borderRadius: "10px",
        padding: "12px",
        cursor: "pointer",
        background: file
          ? "rgba(0,229,160,0.05)"
          : dragging
          ? "var(--panel-hover)"
          : "var(--panel-soft)",
        transition: "all 0.2s ease",
        textAlign: "left",
        minHeight: "74px",
        minWidth: 0,
        width: "100%",
        overflow: "hidden",
        display: "grid",
        gridTemplateColumns: "40px minmax(0, 1fr)",
        alignItems: "center",
        gap: "12px",
      }}
    >
      <input
        ref={ref}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
      />
      <span
        style={{
          width: 40,
          height: 40,
          borderRadius: 8,
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          background: file ? "rgba(0,229,160,0.1)" : "var(--panel)",
          border: file ? "1px solid rgba(0,229,160,0.25)" : "1px solid var(--border)",
          fontSize: "20px",
          flexShrink: 0,
        }}
      >
        {icon}
      </span>
      <div
        style={{
          minWidth: 0,
          maxWidth: "100%",
          overflow: "hidden",
        }}
      >
        <div
          title={file ? file.name : label}
          style={{
            fontFamily: "'Syne', sans-serif",
            fontSize: "12px",
            fontWeight: 700,
            color: file ? "#00e5a0" : "var(--muted-strong)",
            letterSpacing: "0.04em",
            lineHeight: 1.25,
            maxWidth: "100%",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {file ? file.name : label}
        </div>
        {file ? (
          <div
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: "10px",
              color: "rgba(0,150,105,0.85)",
              marginTop: "4px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {(file.size / 1024).toFixed(1)} KB - ready
          </div>
        ) : (
          <div
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: "10px",
              color: "var(--muted-faint)",
              marginTop: "4px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {hint}
          </div>
        )}
      </div>
    </div>
  );
}

export default function FileUpload({ files, onChange }) {
  const update = (key) => (file) => onChange({ ...files, [key]: file });

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.pill}>DOCUMENT UPLOAD</span>
        <span style={styles.sub}>3 files required</span>
      </div>
      <div style={styles.grid}>
        <UploadCard
          label="Invoice"
          icon="🧾"
          accept=".pdf,.png,.jpg,.jpeg"
          file={files.invoice}
          onFile={update("invoice")}
          hint="PDF or image"
        />
        <UploadCard
          label="Payment Proof"
          icon="💳"
          accept=".pdf,.png,.jpg,.jpeg"
          file={files.paymentProof}
          onFile={update("paymentProof")}
          hint="Screenshot or PDF"
        />
        <UploadCard
          label="Bank Statement"
          icon="🏦"
          accept=".csv,.xlsx,.xls"
          file={files.bankStatement}
          onFile={update("bankStatement")}
          hint="CSV or Excel"
        />
      </div>
      <div style={styles.note}>
        <span style={{ color: "var(--muted-faint)", fontSize: "11px", fontFamily: "'IBM Plex Mono', monospace" }}>
          ✦ AI extracts fields - deterministic code handles all financial calculations
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
    minWidth: 0,
    overflow: "hidden",
    boxShadow: "var(--shadow)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "16px",
    gap: "10px",
    minWidth: 0,
  },
  pill: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "var(--muted)",
    whiteSpace: "nowrap",
  },
  sub: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    color: "var(--muted-faint)",
    whiteSpace: "nowrap",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr",
    gap: "10px",
  },
  note: {
    marginTop: "12px",
    textAlign: "center",
  },
};
