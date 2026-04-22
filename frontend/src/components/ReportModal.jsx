import { useEffect } from 'react'
import ChartView from './ChartView'
import DataTable from './DataTable'

const BADGE_CLASS = {
  'Newtract':        'badge-newtract',
  'Business Central':'badge-businesscentral',
  'BambooHR':        'badge-bamboohr',
  'Paywork':         'badge-paywork',
}

function isScalar(v) {
  return v !== null && v !== undefined && typeof v !== 'object'
}

function fmt(val) {
  if (typeof val === 'number')
    return Number.isInteger(val)
      ? val.toLocaleString()
      : val.toLocaleString(undefined, { maximumFractionDigits: 2 })
  return String(val)
}

function humanise(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export default function ReportModal({ report, onClose }) {
  // close on Escape
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const scalarSummary = Object.entries(report.summary ?? {}).filter(
    ([, v]) => isScalar(v)
  )

  const genDate = report.generated_at
    ? new Date(report.generated_at).toLocaleString()
    : ''

  return (
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true">

        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-block">
            <div className="modal-title">{report.report_name}</div>
            <div className="tile-badges" style={{ marginBottom: '0.3rem' }}>
              {report.sources.map(s => (
                <span key={s} className={`badge ${BADGE_CLASS[s] ?? 'badge-newtract'}`}>{s}</span>
              ))}
            </div>
            <div className="modal-meta">
              {report.description} &nbsp;·&nbsp; Generated {genDate}
              {report.filter_applied && (
                <> &nbsp;·&nbsp; Period: <strong>{report.filter_applied}</strong></>
              )}
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <div className="modal-body">

          {/* Summary cards */}
          {scalarSummary.length > 0 && (
            <div>
              <div className="section-label">Summary</div>
              <div className="summary-grid">
                {scalarSummary.map(([k, v]) => (
                  <div key={k} className="summary-card">
                    <div className="summary-label">{humanise(k)}</div>
                    <div className="summary-value">{fmt(v)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chart */}
          {report.chart && (
            <div>
              <div className="section-label">Chart — {report.chart.title}</div>
              <div className="chart-container">
                <ChartView report={report} />
              </div>
            </div>
          )}

          {/* Table */}
          {report.data?.length > 0 && (
            <div>
              <div className="section-label">Data ({report.data.length} rows)</div>
              <DataTable data={report.data} />
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
