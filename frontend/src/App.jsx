import { useState } from "react"
import LandingPage from "./components/LandingPage"
import DigestDashboard from "./components/DigestDashboard"

export default function App() {
  const [view, setView] = useState("landing")
  const [loading, setLoading] = useState(false)
  const [articles, setArticles] = useState([])
  const [filter, setFilter] = useState("all")
  const [error, setError] = useState(null)

  async function fetchDigest() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://localhost:8000/digest?mock=true")
      if (!res.ok) throw new Error("Failed to fetch digest")
      const data = await res.json()
      setArticles(data.articles)
      setView("digest")
    } catch (err) {
      setError("Could not connect to backend. Make sure the server is running.")
    } finally {
      setLoading(false)
    }
  }

  if (view === "landing") {
    return <LandingPage onFetch={fetchDigest} loading={loading} error={error} />
  }

  return (
    <DigestDashboard
      articles={articles}
      filter={filter}
      onFilterChange={setFilter}
    />
  )
}