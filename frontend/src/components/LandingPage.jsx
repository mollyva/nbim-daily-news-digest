import { COLORS } from "../constants"

export default function LandingPage({ onFetch, loading, error }) {
  return (
    <div style={{
      minHeight: "100vh",
      background: COLORS.background,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "2rem"
    }}>
      <div style={{ textAlign: "center", maxWidth: "520px", width: "100%", position: "relative" }}>
        <svg style={{ position: "absolute", right: "-80px", top: "50%", transform: "translateY(-50%)", opacity: 0.05 }} width="340" height="340" viewBox="0 0 340 340" fill="none">
          <circle cx="170" cy="170" r="160" stroke="white" strokeWidth="1.5" />
          <ellipse cx="170" cy="170" rx="80" ry="160" stroke="white" strokeWidth="1.5" />
          <ellipse cx="170" cy="170" rx="160" ry="60" stroke="white" strokeWidth="1.5" />
          <line x1="10" y1="170" x2="330" y2="170" stroke="white" strokeWidth="1" />
          <line x1="170" y1="10" x2="170" y2="330" stroke="white" strokeWidth="1" />
        </svg>

        <p style={{ fontSize: "11px", letterSpacing: "0.12em", textTransform: "uppercase", color: "rgba(255,255,255,0.4)", marginBottom: "1rem", position: "relative", zIndex: 1 }}>
          Norges Bank Investment Management
        </p>
        <h1 style={{ fontSize: "32px", fontWeight: 500, color: "white", marginBottom: "0.75rem", position: "relative", zIndex: 1 }}>
          Daily news digest
        </h1>
        <p style={{ fontSize: "15px", color: "rgba(255,255,255,0.55)", marginBottom: "2rem", position: "relative", zIndex: 1 }}>
          Stay ahead of the news that matters for NBIM's communications team
        </p>

        {error && (
          <p style={{ fontSize: "13px", color: "#fca5a5", marginBottom: "1rem", position: "relative", zIndex: 1 }}>
            {error}
          </p>
        )}

        <button
          onClick={onFetch}
          disabled={loading}
          style={{
            background: "white",
            color: COLORS.background,
            border: "none",
            padding: "12px 28px",
            borderRadius: "8px",
            fontSize: "15px",
            fontWeight: 500,
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1,
            position: "relative",
            zIndex: 1
          }}
        >
          {loading ? "Fetching digest..." : "Get today's digest"}
        </button>
      </div>
    </div>
  )
}