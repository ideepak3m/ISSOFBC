import { useState, useRef, useEffect } from 'react'
import { askChatbot } from '../api'

const SUGGESTIONS = [
  'How do I submit an expense claim?',
  'What is the annual leave policy?',
  'How do I log a service in Newtract?',
  'What programs does ISSofBC offer?',
  'How do I book an interpreter?',
  'What are the grant reporting deadlines?',
  'How do I onboard a new client?',
]

function SourceBadges({ sources }) {
  if (!sources?.length) return null
  return (
    <div className="kb-sources">
      <span className="kb-sources-label">Sources:</span>
      {sources.map((s, i) => (
        <span key={i} className="kb-source-badge">{s.title}</span>
      ))}
    </div>
  )
}

export default function AssistantTab() {
  const [messages,  setMessages]  = useState([])   // [{role:'user'|'assistant', content, sources?}]
  const [input,     setInput]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const bottomRef   = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function buildHistory() {
    return messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return

    setMessages(prev => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)

    try {
      const data = await askChatbot(q, buildHistory())
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: data.answer,
        sources: data.sources,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: `Sorry, I couldn't process that request. ${err.message}`,
        sources: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  function clearChat() {
    setMessages([])
    setInput('')
  }

  const hasMessages = messages.length > 0

  return (
    <div className="kb-wrap">

      {/* ── Header card (shown when empty) ── */}
      {!hasMessages && (
        <div className="kb-welcome">
          <div className="kb-welcome-icon">🤝</div>
          <h2>ISSofBC Internal Knowledge Assistant</h2>
          <p>
            Ask me anything about HR policies, client services, programs, finance,
            IT systems, or step-by-step procedures. I draw on ISSofBC's internal
            knowledge base to give you accurate, specific answers.
          </p>
          <div className="kb-suggestions">
            {SUGGESTIONS.map(s => (
              <button key={s} className="kb-suggestion-chip"
                onClick={() => setInput(s)}>{s}</button>
            ))}
          </div>
        </div>
      )}

      {/* ── Chat thread ── */}
      {hasMessages && (
        <div className="kb-thread">
          <div className="kb-thread-header">
            <span className="section-label" style={{ margin: 0 }}>
              Knowledge Assistant
            </span>
            <button className="chat-clear-btn" onClick={clearChat}>
              New conversation
            </button>
          </div>

          {messages.map((msg, i) => (
            <div key={i} className={`kb-message kb-message--${msg.role}`}>
              {msg.role === 'assistant' && (
                <div className="kb-avatar">🤝</div>
              )}
              <div className="kb-bubble">
                {msg.content.split('\n').map((line, j) => (
                  <p key={j} style={{ margin: '0 0 0.3rem' }}>{line}</p>
                ))}
                {msg.role === 'assistant' && (
                  <SourceBadges sources={msg.sources} />
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="kb-message kb-message--assistant">
              <div className="kb-avatar">🤝</div>
              <div className="kb-bubble kb-bubble--typing">
                <span className="kb-dot" /><span className="kb-dot" /><span className="kb-dot" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}

      {/* ── Input (always visible) ── */}
      <div className={`kb-input-bar${hasMessages ? ' kb-input-bar--sticky' : ''}`}>
        {!hasMessages && (
          <div className="kb-suggestions" style={{ marginBottom: '0.75rem' }}>
            {SUGGESTIONS.slice(0, 4).map(s => (
              <button key={s} className="kb-suggestion-chip"
                onClick={() => setInput(s)}>{s}</button>
            ))}
          </div>
        )}
        <form onSubmit={handleSubmit} className="ai-input-form">
          <input
            className="chat-input"
            placeholder="Ask a question about ISSofBC policies, programs, or procedures…"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="submit-btn" type="submit"
            disabled={loading || !input.trim()}
            style={{ marginTop: 0 }}>
            {loading ? '…' : 'Ask'}
          </button>
        </form>
      </div>

    </div>
  )
}
