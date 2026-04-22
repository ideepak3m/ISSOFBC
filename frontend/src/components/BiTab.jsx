import { useState, useEffect } from 'react'
import { fetchReportList, fetchReport } from '../api'
import ReportTile from './ReportTile'
import ReportModal from './ReportModal'
import FilterBar from './FilterBar'

export default function BiTab() {
  const [reports,  setReports]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState(null)
  const [selected, setSelected] = useState(null)
  const [filter,   setFilter]   = useState({})
  const [paths,    setPaths]    = useState([])

  // Load report path list once
  useEffect(() => {
    fetchReportList()
      .then(({ reports: list }) => setPaths(list.map(r => r.path)))
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  // Re-fetch all reports whenever paths or filter changes
  useEffect(() => {
    if (!paths.length) return
    setLoading(true)
    setError(null)
    Promise.all(paths.map(p => fetchReport(p, filter)))
      .then(setReports)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [paths, filter])

  function handleFilterChange(newFilter) {
    setFilter(newFilter)
    setSelected(null)
  }

  return (
    <>
      <FilterBar filter={filter} onChange={handleFilterChange} />

      {loading && (
        <div className="loading">
          <div className="spinner" />
          Loading reports…
        </div>
      )}

      {error && !loading && (
        <div className="error-box">
          Could not load reports — make sure the API is running on port 8000.<br />
          <strong>{error}</strong>
        </div>
      )}

      {!loading && !error && (
        <div className="report-grid">
          {reports.map(r => (
            <ReportTile key={r.report_id} report={r} onClick={() => setSelected(r)} />
          ))}
        </div>
      )}

      {selected && (
        <ReportModal report={selected} onClose={() => setSelected(null)} />
      )}
    </>
  )
}
