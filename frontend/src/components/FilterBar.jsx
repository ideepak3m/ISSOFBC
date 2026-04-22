import { useState } from 'react'

const CURRENT_YEAR = new Date().getFullYear()
const QUICK_YEARS  = [CURRENT_YEAR, CURRENT_YEAR - 1, CURRENT_YEAR - 2]

export default function FilterBar({ filter, onChange }) {
  const [showCustom, setShowCustom] = useState(false)
  const [startDate,  setStartDate]  = useState('')
  const [endDate,    setEndDate]    = useState('')

  function selectYear(y) {
    setShowCustom(false)
    onChange({ year: y })
  }

  function selectAllTime() {
    setShowCustom(false)
    onChange({})
  }

  function applyCustom() {
    if (!startDate && !endDate) return
    onChange({ start_date: startDate || undefined, end_date: endDate || undefined })
  }

  const activeYear   = filter.year
  const isAllTime    = !filter.year && !filter.start_date && !filter.end_date
  const isCustom     = !filter.year && (filter.start_date || filter.end_date)

  return (
    <div className="filter-bar">
      <span className="filter-label">Period:</span>

      <div className="filter-pills">
        <button
          className={`filter-pill${isAllTime ? ' active' : ''}`}
          onClick={selectAllTime}
        >All Time</button>

        {QUICK_YEARS.map(y => (
          <button
            key={y}
            className={`filter-pill${activeYear === y ? ' active' : ''}`}
            onClick={() => selectYear(y)}
          >{y}</button>
        ))}

        <button
          className={`filter-pill${isCustom || showCustom ? ' active' : ''}`}
          onClick={() => setShowCustom(v => !v)}
        >Custom…</button>
      </div>

      {showCustom && (
        <div className="filter-custom">
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            className="filter-date-input"
          />
          <span className="filter-to">to</span>
          <input
            type="date"
            value={endDate}
            onChange={e => setEndDate(e.target.value)}
            className="filter-date-input"
          />
          <button className="filter-apply-btn" onClick={applyCustom}>Apply</button>
        </div>
      )}
    </div>
  )
}
