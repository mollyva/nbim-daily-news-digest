// Colors used throughout the app
export const COLORS = {
  background: "#1a2e44",    // dark navy — NBIM brand color, used everywhere
  card: "#f5f0e8",          // warm beige — contrasts nicely against navy background
  cardBorder: "rgba(0,0,0,0.08)",
  textPrimary: "#1a2e44",   // dark navy text on beige cards
  textSecondary: "#6b7280", // muted gray for secondary info
  textMuted: "#9ca3af",     // very muted for metadata
  link: "#185fa5",          // blue link color
}

// Action badge colors — each action has a background, text color and border
export const ACTION_CONFIG = {
  "Recommend public response": {
    bg: "#fee2e2",
    color: "#991b1b",
    border: "#fca5a5"
  },
  "Alert portfolio manager": {
    bg: "#ffedd5",
    color: "#92400e",
    border: "#fdba74"
  },
  "Comms team action required": {
    bg: "#fef9c3",
    color: "#713f12",
    border: "#fde047"
  },
  "Monitor only": {
    bg: "#dcfce7",
    color: "#14532d",
    border: "#86efac"
  }
}