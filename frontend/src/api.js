const BASE = ''  // proxied to http://localhost:8000 via vite config

export async function fetchReportList() {
  const res = await fetch(`${BASE}/api/reports`)
  if (!res.ok) throw new Error('Failed to fetch report list')
  return res.json()
}

export async function fetchReport(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`Failed to fetch report: ${path}`)
  return res.json()
}

export async function runAdhocQuery(userQuery) {
  const res = await fetch(`${BASE}/api/adhoc`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: userQuery }),
  })
  if (res.status === 404) throw new Error('COMING_SOON')
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Query failed')
  }
  return res.json()
}
