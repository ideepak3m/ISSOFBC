const BASE = ''  // proxied to http://localhost:8000 via vite config

export async function fetchReportList() {
  const res = await fetch(`${BASE}/api/reports`)
  if (!res.ok) throw new Error('Failed to fetch report list')
  return res.json()
}

export async function fetchReport(path, filter = {}) {
  const params = new URLSearchParams()
  if (filter.year)       params.set('year',       filter.year)
  if (filter.start_date) params.set('start_date', filter.start_date)
  if (filter.end_date)   params.set('end_date',   filter.end_date)
  const qs  = params.toString()
  const url = qs ? `${BASE}${path}?${qs}` : `${BASE}${path}`
  const res = await fetch(url)
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
