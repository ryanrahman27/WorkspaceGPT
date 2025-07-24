import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  MessageSquare, 
  Brain, 
  Search, 
  Settings, 
  FileText, 
  CheckSquare, 
  BarChart3,
  Upload,
  Loader2,
  AlertCircle,
  CheckCircle,
  Bot
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('query');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setStats(response.data.stats);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleSubmitQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query: query.trim()
      });
      
      setResults(response.data);
      setActiveTab('results');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      fetchStats(); // Refresh stats after upload
      alert('Document uploaded successfully!');
    } catch (err) {
      alert('Failed to upload document: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Bot className="logo-icon" />
            <h1>WorkspaceGPT</h1>
          </div>
          <p className="tagline">Multi-Agent AI Assistant with PDF Retrieval</p>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          <MessageSquare size={20} />
          Query
        </button>
        <button 
          className={`nav-tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          <BarChart3 size={20} />
          Results
        </button>
        <button 
          className={`nav-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          <FileText size={20} />
          Documents
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'query' && (
          <div className="query-section">
            <div className="query-card">
              <h2>Ask WorkspaceGPT</h2>
              <p>Enter your question and let our multi-agent system help you!</p>
              
              <form onSubmit={handleSubmitQuery} className="query-form">
                <div className="input-group">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Example: Summarize my onboarding and create a checklist"
                    className="query-input"
                    rows={4}
                    disabled={isLoading}
                  />
                  <button 
                    type="submit" 
                    className="submit-btn"
                    disabled={isLoading || !query.trim()}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="spinning" size={20} />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Brain size={20} />
                        Process Query
                      </>
                    )}
                  </button>
                </div>
              </form>

              {error && (
                <div className="error-message">
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              <div className="example-queries">
                <h3>Example Queries:</h3>
                <div className="examples">
                  <button 
                    className="example-btn"
                    onClick={() => setQuery("Summarize my onboarding and create a checklist")}
                  >
                    Summarize onboarding and create checklist
                  </button>
                  <button 
                    className="example-btn"
                    onClick={() => setQuery("What are the company values and policies?")}
                  >
                    Company values and policies
                  </button>
                  <button 
                    className="example-btn"
                    onClick={() => setQuery("Create a task list for my first week")}
                  >
                    First week task list
                  </button>
                </div>
              </div>
            </div>

            {stats && (
              <div className="stats-card">
                <h3>System Status</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <FileText size={24} />
                    <div>
                      <div className="stat-value">{stats.num_source_files || 0}</div>
                      <div className="stat-label">Documents</div>
                    </div>
                  </div>
                  <div className="stat-item">
                    <Search size={24} />
                    <div>
                      <div className="stat-value">{stats.total_documents || 0}</div>
                      <div className="stat-label">Chunks</div>
                    </div>
                  </div>
                  <div className="stat-item">
                    <CheckCircle size={24} />
                    <div>
                      <div className="stat-value">{stats.status === 'initialized' ? 'Ready' : 'Loading'}</div>
                      <div className="stat-label">Status</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'results' && (
          <div className="results-section">
            {results ? (
              <div className="results-content">
                <div className="results-header">
                  <h2>Processing Results</h2>
                  <div className={`status-badge ${results.success ? 'success' : 'error'}`}>
                    {results.success ? 'Success' : 'Failed'}
                  </div>
                </div>

                <div className="query-display">
                  <strong>Query:</strong> {results.user_query}
                </div>

                {results.plan && (
                  <div className="plan-section">
                    <h3>📋 Execution Plan</h3>
                    <p className="plan-analysis">{results.plan.analysis}</p>
                    <div className="steps">
                      {results.plan.steps.map((step, index) => (
                        <div key={index} className="step-card">
                          <div className="step-header">
                            <span className="step-number">{step.step_number}</span>
                            <span className="agent-badge">{step.agent}</span>
                          </div>
                          <p className="step-description">{step.description}</p>
                          <div className="step-action">{step.action}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {results.step_results && (
                  <div className="step-results-section">
                    <h3>⚡ Execution Results</h3>
                    {results.step_results.map((stepResult, index) => (
                      <div key={index} className={`step-result ${stepResult.success ? 'success' : 'error'}`}>
                        <div className="step-result-header">
                          <span>Step {stepResult.step_number}: {stepResult.description}</span>
                          <span className={`status ${stepResult.success ? 'success' : 'error'}`}>
                            {stepResult.success ? '✅' : '❌'}
                          </span>
                        </div>
                        {stepResult.result && stepResult.result.result && (
                          <div className="step-result-content">
                            {stepResult.agent === 'Retriever' && stepResult.result.summary && (
                              <p className="result-summary">{stepResult.result.summary}</p>
                            )}
                            {stepResult.agent === 'Executor' && stepResult.result.result.message && (
                              <p className="result-message">{stepResult.result.result.message}</p>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {results.final_summary && (
                  <div className="final-summary">
                    <h3>📊 Summary</h3>
                    <div className="summary-stats">
                      <div className="summary-item">
                        <strong>Total Steps:</strong> {results.final_summary.total_steps}
                      </div>
                      <div className="summary-item">
                        <strong>Successful:</strong> {results.final_summary.successful_steps}
                      </div>
                      <div className="summary-item">
                        <strong>Documents Retrieved:</strong> {results.final_summary.retrieved_documents}
                      </div>
                    </div>
                    {results.final_summary.key_achievements && (
                      <div className="achievements">
                        <h4>Key Achievements:</h4>
                        <ul>
                          {results.final_summary.key_achievements.map((achievement, index) => (
                            <li key={index}>{achievement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="no-results">
                <Brain size={48} />
                <h3>No Results Yet</h3>
                <p>Submit a query to see the multi-agent processing results here.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-section">
            <div className="documents-header">
              <h2>Document Management</h2>
              <FileUpload onUpload={handleFileUpload} />
            </div>
            
            {stats && stats.source_files && (
              <div className="documents-list">
                <h3>Available Documents ({stats.source_files.length})</h3>
                {stats.source_files.map((filename, index) => (
                  <div key={index} className="document-item">
                    <FileText size={20} />
                    <span>{filename}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function FileUpload({ onUpload }) {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
      onUpload(files[0]);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      onUpload(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  return (
    <div 
      className={`file-upload ${dragOver ? 'drag-over' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <Upload size={24} />
      <span>Drop PDF here or </span>
      <label className="file-select-btn">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        choose file
      </label>
    </div>
  );
}

export default App; 