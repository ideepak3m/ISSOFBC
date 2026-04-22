import { useState } from 'react'
import { runAdhocQuery } from '../api'
import ChartView from './ChartView'
import DataTable from './DataTable'

const EXAMPLES = [
  'How many beneficiaries are from Syria?',
  'What is the job placement rate per program?',
  'Show total expenses by category for 2024',
  'Which staff member delivered the most services?',
  'What is our total payroll cost year to date?',
]

export default function AiTab() {
  const [query, setQuery]     = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [comingSoon, setComingSoon] = useState(false)
  const [error, setError]     = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setResult(null)
    setError(null)
    setComingSoon(false)

    try {
      const data = await runAdhocQuery(query.trim())
      setResult(data)
    } catch (err) {
      if (err.message === 'COMING_SOON') setComingSoon(true)
      else setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ai-wrap">

      {/* Input card */}
      <div className="ai-input-card">
        <h2>Ask a Question About Your Data</h2>
        <p>Type a question in plain English. The AI will generate a SQL query, run it, and return a summary, table, and chart.</p>

        <form onSubmit={handleSubmit}>
          <textarea
            className="query-textarea"
            placeholder="e.g. How many active beneficiaries do we have from each country?"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit(e) }}
          />

          <div className="example-queries">
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', alignSelf: 'center' }}>Try:</span>
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                type="button"
                className="example-chip"
                onClick={() => setQuery(ex)}
              >
                {ex}
              </button>
            ))}
          </div>

          <button className="submit-btn" type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Thinking…' : 'Generate Report'}
          </button>
        </form>
      </div>

      {/* Loading */}
      {loading && (
        <div className="loading">
          <div className="spinner" />
          Generating SQL and running query…
        </div>
      )}

      {/* Coming soon */}
      {comingSoon && (
        <div className="coming-soon-box">
          <div className="cs-icon">🤖</div>
          <h3>AI Query — Coming Soon</h3>
          <p>
            The natural language → SQL endpoint is the next feature being built.
            The UI is ready and will display results here as soon as the API endpoint is live.
          </p>
        </div>
      )}

      {/* Error */}
      {error && <div className="error-box">{error}</div>}

      {/* Results */}
      {result && (
        <div className="ai-result-card">

          {/* Summary */}
          {result.summary && (
            <div>
              <div className="section-label">Summary</div>
              <div className="ai-summary">{result.summary}</div>
            </div>
          )}

          {/* Generated SQL */}
          {result.generated_sql && (
            <div>
              <div className="section-label">Generated SQL</div>
              <div className="ai-sql-block">
                <pre>{result.generated_sql}</pre>
              </div>
            </div>
          )}

          {/* Chart */}
          {result.chart && (
            <div>
              <div className="section-label">Chart — {result.chart.title}</div>
              <div className="chart-container">
                <ChartView report={result} />
              </div>
            </div>
          )}

          {/* Table */}
          {result.data?.length > 0 && (
            <div>
              <div className="section-label">Data ({result.data.length} rows)</div>
              <DataTable data={result.data} />
            </div>
          )}

        </div>
      )}
    </div>
  )
}
