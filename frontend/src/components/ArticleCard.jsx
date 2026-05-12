import ActionBadge from "./ActionBadge"
import { COLORS } from "../constants"

export default function ArticleCard({ article }) {
  const formatted = article.published_at
    ? new Date(article.published_at).toLocaleDateString("en-GB", {
        day: "numeric", month: "short", year: "numeric"
      })
    : ""

  return (
    <div style={{
      background: COLORS.card,
      border: `0.5px solid ${COLORS.cardBorder}`,
      borderRadius: "12px",
      padding: "1rem 1.25rem",
      display: "flex",
      flexDirection: "column",
      gap: "8px",
      justifyContent: "space-between",
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "10px" }}>
        <span style={{ fontSize: "13px", fontWeight: 500, lineHeight: 1.45, color: COLORS.textPrimary }}>
          {article.title}
        </span>
        <ActionBadge action={article.action} />
      </div>

      <p style={{ fontSize: "12px", color: COLORS.textSecondary, lineHeight: 1.6, margin: 0 }}>
        {article.summary}
      </p>

      <div style={{
        fontSize: "11px",
        color: COLORS.textSecondary,
        fontStyle: "italic",
        padding: "6px 10px",
        background: "rgba(0,0,0,0.04)",
        borderRadius: "6px",
        lineHeight: 1.5
      }}>
        {article.action_reasoning}
      </div>

      <div style={{
        display: "flex",
        gap: "12px",
        fontSize: "11px",
        color: COLORS.textMuted,
        alignItems: "center",
        paddingTop: "6px",
        borderTop: `0.5px solid rgba(0,0,0,0.08)`,
        flexWrap: "wrap"
      }}>
        <span>{article.source}{article.author ? ` · ${article.author}` : ""}</span>
        <span>{formatted}</span>
        {article.url && (
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            style={{ color: COLORS.link, textDecoration: "none", marginLeft: "auto" }}
          >
            Read article ↗
          </a>
        )}
      </div>
    </div>
  )
}