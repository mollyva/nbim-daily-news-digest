import { ACTION_CONFIG } from "../constants"

export default function ActionBadge({ action }) {
  const config = ACTION_CONFIG[action] || {}
  return (
    <span style={{
      background: config.bg,
      color: config.color,
      border: `0.5px solid ${config.border}`,
      fontSize: "11px",
      fontWeight: 500,
      padding: "3px 10px",
      borderRadius: "99px",
      whiteSpace: "nowrap",
      flexShrink: 0
    }}>
      {action}
    </span>
  )
}