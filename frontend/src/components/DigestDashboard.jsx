import { COLORS } from "../constants"
import StatsSummary from "./StatsSummary"
import ArticleCard from "./ArticleCard"

export default function DigestDashboard({ articles, filter, onFilterChange }) {
  const filtered = filter === "all" ? articles : articles.filter(a => a.action === filter)

  const counts = {
    total: articles.length,
    c1: articles.filter(a => a.action === "Recommend public response").length,
    c2: articles.filter(a => a.action === "Alert portfolio manager").length,
    c3: articles.filter(a => a.action === "Comms team action required").length,
    c4: articles.filter(a => a.action === "Monitor only").length,
  }

  return (
    <div style={{ minHeight: "100vh", background: COLORS.background, padding: "2rem" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>

        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "1.5rem" }}>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="white" strokeWidth="1.2" opacity="0.5" />
            <ellipse cx="16" cy="16" rx="7" ry="14" stroke="white" strokeWidth="1.2" opacity="0.5" />
            <ellipse cx="16" cy="16" rx="14" ry="5.5" stroke="white" strokeWidth="1.2" opacity="0.5" />
          </svg>
          <div>
            <div style={{ fontSize: "18px", fontWeight: 500, color: "white" }}>NBIM daily news digest</div>
            <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginTop: "2px" }}>
              {new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
            </div>
          </div>
        </div>

        <StatsSummary counts={counts} />

        <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "1rem" }}>
          <span style={{ fontSize: "13px", color: "rgba(255,255,255,0.5)" }}>Filter:</span>
          <select
            value={filter}
            onChange={e => onFilterChange(e.target.value)}
            style={{
                fontSize: "13px",
                padding: "6px 10px",
                borderRadius: "8px",
                border: `0.5px solid ${COLORS.cardBorder}`,
                background: COLORS.card,
                color: COLORS.textPrimary,
                cursor: "pointer"
            }}
          >
            <option value="all">All actions</option>
            <option value="Recommend public response">Recommend public response</option>
            <option value="Alert portfolio manager">Alert portfolio manager</option>
            <option value="Comms team action required">Comms team action required</option>
            <option value="Monitor only">Monitor only</option>
          </select>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>
          {filtered.length === 0
            ? <p style={{ color: COLORS.card, fontSize: "18px", gridColumn: "1/-1", textAlign: "center", padding: "2rem" }}>
                No articles match this filter
              </p>
            : filtered.map((a, i) => <ArticleCard key={i} article={a} />)
          }
        </div>

      </div>
    </div>
  )
}