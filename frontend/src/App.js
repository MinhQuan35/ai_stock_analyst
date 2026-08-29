import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [tab, setTab] = useState('chat');

  useEffect(() => {
    checkHealth();
    loadMetrics();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/health`);
      setHealth(res.data);
    } catch (e) {
      setHealth({ status: 'error', pipeline_initialized: false });
    }
  };

  const loadMetrics = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/metrics`);
      setMetrics(res.data);
    } catch (e) {
      console.error('Failed to load metrics', e);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/api/chat`, {
        message: input,
        use_reranker: true,
      });
      const agentMsg = { role: 'agent', content: res.data.response };
      setMessages((prev) => [...prev, agentMsg]);
      loadMetrics();
    } catch (e) {
      const errorMsg = {
        role: 'agent',
        content: 'Error: ' + (e.response?.data?.detail || e.message),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const buildIndex = async () => {
    if (!window.confirm('Build/rebuild index?')) return;
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/index`, { force_rebuild: true });
      alert('Index built successfully!');
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const resetMetrics = async () => {
    await axios.post(`${API_BASE}/api/metrics/reset`);
    loadMetrics();
  };

  return (
    <div className="App">
      <header className="header">
        <h1>📊 RAG Stock Analyst</h1>
        <div className="status">
          <span className={`status-dot ${health?.status === 'healthy' ? 'ok' : 'err'}`}></span>
          {health?.status || 'checking...'}
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === 'chat' ? 'active' : ''} onClick={() => setTab('chat')}>
          Chat
        </button>
        <button className={tab === 'metrics' ? 'active' : ''} onClick={() => setTab('metrics')}>
          RAG Metrics
        </button>
        <button className={tab === 'admin' ? 'active' : ''} onClick={() => setTab('admin')}>
          Admin
        </button>
      </nav>

      <main className="main">
        {tab === 'chat' && (
          <div className="chat">
            <div className="messages">
              {messages.length === 0 && (
                <div className="welcome">
                  <h2>Ask about stocks!</h2>
                  <p>Try: "What is P/E ratio?" or "When is RSI overbought?"</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <div className="role">{msg.role === 'user' ? 'You' : 'Agent'}</div>
                  <div className="content">{msg.content}</div>
                </div>
              ))}
              {loading && <div className="message agent"><div className="content">Thinking...</div></div>}
            </div>
            <div className="input-area">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about stocks..."
                disabled={loading}
              />
              <button onClick={sendMessage} disabled={loading || !input.trim()}>
                Send
              </button>
            </div>
          </div>
        )}

        {tab === 'metrics' && (
          <div className="metrics">
            <h2>RAG Metrics</h2>
            {metrics ? (
              <>
                <div className="metric-group">
                  <h3>Retrieval</h3>
                  <div className="metric">
                    <span>Precision@K</span>
                    <strong>{(metrics.retrieval.precision_at_k * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="metric">
                    <span>Recall@K</span>
                    <strong>{(metrics.retrieval.recall_at_k * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="metric">
                    <span>MRR</span>
                    <strong>{metrics.retrieval.mrr.toFixed(4)}</strong>
                  </div>
                  <div className="metric">
                    <span>NDCG</span>
                    <strong>{metrics.retrieval.ndcg.toFixed(4)}</strong>
                  </div>
                </div>

                <div className="metric-group">
                  <h3>Generation</h3>
                  <div className="metric">
                    <span>Faithfulness</span>
                    <strong>{(metrics.generation.faithfulness * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="metric">
                    <span>Relevancy</span>
                    <strong>{(metrics.generation.relevancy * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="metric">
                    <span>Answer Correctness</span>
                    <strong>{(metrics.generation.answer_correctness * 100).toFixed(1)}%</strong>
                  </div>
                </div>

                <div className="metric-group">
                  <h3>Quality</h3>
                  <div className="metric">
                    <span>Hallucination Rate</span>
                    <strong className={metrics.hallucination_rate < 0.2 ? 'good' : 'bad'}>
                      {(metrics.hallucination_rate * 100).toFixed(1)}%
                    </strong>
                  </div>
                </div>

                <div className="metric-group">
                  <h3>Summary</h3>
                  <div className="metric">
                    <span>Total Queries</span>
                    <strong>{metrics.summary.total_queries}</strong>
                  </div>
                </div>

                <button onClick={resetMetrics} className="reset-btn">
                  Reset Metrics
                </button>
              </>
            ) : (
              <p>No metrics yet. Chat with the agent to generate metrics.</p>
            )}
          </div>
        )}

        {tab === 'admin' && (
          <div className="admin">
            <h2>Admin</h2>
            <div className="admin-card">
              <h3>Index Management</h3>
              <p>Build or rebuild the Qdrant vector index.</p>
              <button onClick={buildIndex} disabled={loading}>
                {loading ? 'Building...' : 'Build Index'}
              </button>
            </div>
            <div className="admin-card">
              <h3>Stack</h3>
              <ul>
                <li>✅ Azure OpenAI (GPT-4o + Embeddings)</li>
                <li>✅ Qdrant Cloud (Vector DB)</li>
                <li>✅ Cohere Rerank v4.0 Fast</li>
                <li>✅ FastAPI Backend</li>
                <li>✅ React Frontend</li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
