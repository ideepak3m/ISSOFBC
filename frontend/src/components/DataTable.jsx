function fmt(val) {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  if (typeof val === 'number') {
    return Number.isInteger(val)
      ? val.toLocaleString()
      : val.toLocaleString(undefined, { maximumFractionDigits: 2 })
  }
  return String(val)
}

function isNumeric(val) {
  return typeof val === 'number'
}

function humanise(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export default function DataTable({ data }) {
  if (!data?.length) return <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No data.</p>

  const cols = Object.keys(data[0]).filter(k => !Array.isArray(data[0][k]) && typeof data[0][k] !== 'object')

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {cols.map(c => (
              <th key={c} className={isNumeric(data[0][c]) ? 'num' : ''}>
                {humanise(c)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {cols.map(c => (
                <td key={c} className={isNumeric(row[c]) ? 'num' : ''}>
                  {fmt(row[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
