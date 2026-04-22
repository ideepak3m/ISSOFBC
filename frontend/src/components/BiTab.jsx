import { useState, useEffect } from 'react'
import { fetchReportList, fetchReport } from '../api'
import ReportTile from './ReportTile'
import ReportModal from './ReportModal'

export default function BiTab() {
  const [reports, setReports]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const { reports: list } = await fetchReportList()
        const detailed = await Promise.all(list.map(r => fetchReport(r.path)))
        setReports(detailed)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return (
    <div className="loading">
      <div className="spinner" />
      Loading reports…
    </div>
  )

  if (error) return (
    <div className="error-box">
      Could not load reports — make sure the API is running on port 8000.<br />
      <strong>{error}</strong>
    </div>
  )

  return (
    <>
      <div className="report-grid">
        {reports.map(r => (
          <ReportTile key={r.report_id} report={r} onClick={() => setSelected(r)} />
        ))}
      </div>

      {selected && (
        <ReportModal report={selected} onClose={() => setSelected(null)} />
      )}
    </>
  )
}
