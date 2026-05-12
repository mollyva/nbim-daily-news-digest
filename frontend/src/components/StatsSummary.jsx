import { COLORS } from "../constants"

const STAT_ITEMS = [
  { key: "total",  label: "Total articles",   color: COLORS.textSecondary },
  { key: "c1",     label: "Public response",  color: "#991b1b" },
  { key: "c2",     label: "Portfolio alerts", color: "#92400e" },
  { key: "c3",     label: "Comms action",     color: "#713f12" },
  { key: "c4",     label: "Monitor only",     color: "#14532d" },
]

export default function StatsSummary({ counts }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "8px", marginBottom: "1.5rem" }}>
      {STAT_ITEMS.map(s => (
        <div key={s.key} style={{
          background: COLORS.card,
          border: `0.5px solid ${COLORS.cardBorder}`,
          borderRadius: "8px",
          padding: "0.75rem 1rem"
        }}>
          <div style={{ fontSize: "11px", color: s.color, marginBottom: "4px" }}>{s.label}</div>
          <div style={{ fontSize: "22px", fontWeight: 500, color: COLORS.textPrimary }}>{counts[s.key]}</div>
        </div>
      ))}
    </div>
  )
}