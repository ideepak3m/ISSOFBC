import ChartView from './ChartView'

const BADGE_CLASS = {
  'Newtract':        'badge-newtract',
  'Business Central':'badge-businesscentral',
  'BambooHR':        'badge-bamboohr',
  'Paywork':         'badge-paywork',
}

export default function ReportTile({ report, onClick }) {
  const genDate = report.generated_at
    ? new Date(report.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : ''

  return (
    <div className="tile" onClick={onClick} role="button" tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}>

      <div className="tile-header">
        <div className="tile-title">{report.report_name}</div>
        <div className="tile-badges">
          {report.sources.map(s => (
            <span key={s} className={`badge ${BADGE_CLASS[s] ?? 'badge-newtract'}`}>{s}</span>
          ))}
        </div>
      </div>

      <div className="tile-chart">
        {report.chart
          ? <ChartView report={report} thumbnail />
          : <div className="no-chart-thumb">📊</div>
        }
      </div>

      <div className="tile-footer">
        {report.description?.slice(0, 80)}{report.description?.length > 80 ? '…' : ''}
        <span style={{ float: 'right', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {report.filter_applied && report.filter_applied !== 'All Time' && (
            <span className="filter-pill active" style={{ fontSize: '0.62rem', padding: '2px 8px' }}>
              {report.filter_applied}
            </span>
          )}
          {genDate}
        </span>
      </div>
    </div>
  )
}
