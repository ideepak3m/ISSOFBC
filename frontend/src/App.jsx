import { useState } from 'react'
import BiTab from './components/BiTab'
import AiTab from './components/AiTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('bi')

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">📊</span>
            <div>
              <h1>IISofBC Analytics</h1>
              <p>Newtract · Business Central · BambooHR · Paywork</p>
            </div>
          </div>
          <nav className="tab-bar">
            <button
              className={`tab-btn ${activeTab === 'bi' ? 'active' : ''}`}
              onClick={() => setActiveTab('bi')}
            >
              BI Reports
            </button>
            <button
              className={`tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
              onClick={() => setActiveTab('ai')}
            >
              AI Query
            </button>
          </nav>
        </div>
      </header>

      <main className="main">
        {activeTab === 'bi' ? <BiTab /> : <AiTab />}
      </main>
    </div>
  )
}
