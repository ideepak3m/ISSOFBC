import { useState, useRef, useEffect } from 'react'
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

function ResultCard({ turn }) {
  const [sqlOpen, setSqlOpen] = useState(false)
  const { query, result, error } = turn

  return (
    <div className="chat-turn">
      {/* User bubble */}
      <div className="chat-user-bubble">{query}</div>

      {/* AI response */}
      <div className="chat-ai-bubble">
        {error ? (
          <div className="chat-error">{error}</div>
        ) : result ? (
          <>
            {result.summary && (
              <div className="chat-summary">{result.summary}</div>
            )}

            {/* SQL toggle */}
            <button className="sql-toggle" onClick={() => setSqlOpen(v => !v)}>
              {sqlOpen ? '▾' : '▸'} Generated SQL
            </button>
            {sqlOpen && (
              <div className="ai-sql-block">
                <pre>{result.generated_sql}</pre>
              </div>
            )}

            {/* Chart */}
            {result.chart && (
              <div className="chat-chart-wrap">
                <div className="chart-container">
                  <ChartView report={result} />
                </div>
              </div>
            )}

            {/* Table */}
            {result.data?.length > 0 && (
              <div>
                <div className="section-label" style={{ marginTop: '1rem' }}>
                  {result.data.length} row{result.data.length !== 1 ? 's' : ''}
                </div>
                <DataTable data={result.data} />
              </div>
            )}
          </>
        ) : (
          <div className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
        )}
      </div>
    </div>
  )
}

export default function AiTab() {
  const [conversation, setConversation] = useState([])   // [{id, query, result, error}]
  const [query,    setQuery]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const bottomRef  = useRef(null)

  // Scroll to latest message after each update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation])

  // history sent to the API: prior successful turns only
  function buildHistory() {
    return conversation
      .filter(t => t.result?.generated_sql)
      .map(t => ({ query: t.query, sql: t.result.generated_sql }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const q = query.trim()
    if (!q || loading) return

    const id = Date.now()
    setConversation(prev => [...prev, { id, query: q, result: null, error: null }])
    setQuery('')
    setLoading(true)

    try {
      const data = await runAdhocQuery(q, buildHistory())
      setConversation(prev =>
        prev.map(t => t.id === id ? { ...t, result: data } : t)
      )
    } catch (err) {
      setConversation(prev =>
        prev.map(t => t.id === id ? { ...t, error: err.message } : t)
      )
    } finally {
      setLoading(false)
    }
  }

  function clearConversation() {
    setConversation([])
    setQuery('')
  }

  const hasHistory = conversation.length > 0

  return (
    <div className="ai-wrap">

      {/* ── Empty state ── */}
      {!hasHistory && (
        <div className="ai-input-card">
          <h2>Ask a Question About Your Data</h2>
          <p>
            Type a question in plain English. The AI will generate SQL, run it,
            and return a summary, chart, and table. Follow-up questions remember context.
          </p>
          <div className="example-queries">
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', alignSelf: 'center' }}>Try:</span>
            {EXAMPLES.map(ex => (
              <button key={ex} type="button" className="example-chip"
                onClick={() => setQuery(ex)}>{ex}</button>
            ))}
          </div>
        </div>
      )}

      {/* ── Conversation thread ── */}
      {hasHistory && (
        <div className="chat-thread">
          <div className="chat-thread-header">
            <span className="section-label" style={{ margin: 0 }}>
              {conversation.length} message{conversation.length !== 1 ? 's' : ''}
            </span>
            <button className="chat-clear-btn" onClick={clearConversation}>
              Clear conversation
            </button>
          </div>

          {conversation.map(turn => (
            <ResultCard key={turn.id} turn={turn} />
          ))}

          <div ref={bottomRef} />
        </div>
      )}

      {/* ── Input (always visible) ── */}
      <div className={`ai-input-bar${hasHistory ? ' ai-input-bar--sticky' : ''}`}>
        <form onSubmit={handleSubmit} className="ai-input-form">
          <input
            className="chat-input"
            placeholder={hasHistory
              ? 'Ask a follow-up question…'
              : 'e.g. How many active beneficiaries do we have from each country?'}
            value={query}
            onChange={e => setQuery(e.target.value)}
            disabled={loading}
          />
          <button className="submit-btn" type="submit" disabled={loading || !query.trim()}>
            {loading ? '…' : 'Ask'}
          </button>
        </form>

        {!hasHistory && (
          <div className="example-queries" style={{ marginTop: '0.5rem' }}>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', alignSelf: 'center' }}>Try:</span>
            {EXAMPLES.map(ex => (
              <button key={ex} type="button" className="example-chip"
                onClick={() => setQuery(ex)}>{ex}</button>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
