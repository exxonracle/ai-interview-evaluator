import React, { useState, useEffect, useCallback } from 'react';

function RecruiterDashboard({ onViewCandidate }) {
  const [candidates, setCandidates] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('rankings');
  const [compareIds, setCompareIds] = useState([]);
  const [compareData, setCompareData] = useState([]);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [candResp, rankResp] = await Promise.all([
        fetch('http://127.0.0.1:8000/candidates'),
        fetch('http://127.0.0.1:8000/rankings'),
      ]);
      const candData = await candResp.json();
      const rankData = await rankResp.json();
      setCandidates(candData.candidates || []);
      setRankings(rankData.rankings || []);
    } catch (err) {
      setError('Failed to fetch data. Ensure the backend is running.');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this candidate and all their data?')) return;
    try {
      await fetch(`http://127.0.0.1:8000/candidates/${id}`, { method: 'DELETE' });
      fetchData();
      setCompareIds((prev) => prev.filter((cid) => cid !== id));
    } catch (err) {
      alert('Failed to delete candidate.');
    }
  };

  const handleDownloadPdf = (id, name) => {
    const url = `http://127.0.0.1:8000/candidates/${id}/report`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `evaluation_report_${name.replace(/\s/g, '_')}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleCompare = async (id) => {
    let newIds;
    if (compareIds.includes(id)) {
      newIds = compareIds.filter((cid) => cid !== id);
    } else {
      newIds = [...compareIds, id];
    }
    setCompareIds(newIds);

    // Fetch full data for comparison
    if (newIds.length >= 2) {
      try {
        const details = await Promise.all(
          newIds.map((cid) => fetch(`http://127.0.0.1:8000/candidates/${cid}`).then(r => r.json()))
        );
        setCompareData(details);
      } catch (err) {
        setCompareData([]);
      }
    } else {
      setCompareData([]);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'excellent';
    if (score >= 5) return 'good';
    return 'needs-improvement';
  };

  const getMedalIcon = (rank) => {
    if (rank === 1) return 'Rank 1';
    if (rank === 2) return 'Rank 2';
    if (rank === 3) return 'Rank 3';
    return `#${rank}`;
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="gradient-text">AI Candidate Evaluator Dashboard</h1>
          <p className="subtitle">Loading candidate data...</p>
        </div>
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px' }}>
          <span className="spinner" style={{ width: '40px', height: '40px' }}></span>
          <p style={{ color: '#94a3b8', marginTop: '20px' }}>Fetching evaluations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="gradient-text">AI Candidate Evaluator Dashboard</h1>
        <p className="subtitle">
          {candidates.length} candidate{candidates.length !== 1 ? 's' : ''} evaluated
        </p>
      </div>

      {error && (
        <div className="error-banner glass-card">
          <span></span> {error}
          <button onClick={fetchData} className="retry-btn">Retry</button>
        </div>
      )}

      {candidates.length === 0 && !error ? (
        <div className="glass-card empty-state">
          <div className="empty-icon"></div>
          <h3>No candidates yet</h3>
          <p style={{ color: '#94a3b8' }}>
            Go to Candidate Upload to evaluate your first candidate.
          </p>
        </div>
      ) : (
        <>
          {/* Tab Switcher */}
          <div className="dash-tabs">
            <button
              className={`dash-tab ${activeTab === 'rankings' ? 'active' : ''}`}
              onClick={() => setActiveTab('rankings')}
              id="tab-rankings"
            >
              Rankings
            </button>
            <button
              className={`dash-tab ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
              id="tab-all"
            >
              All Candidates
            </button>
            <button
              className={`dash-tab ${activeTab === 'compare' ? 'active' : ''}`}
              onClick={() => setActiveTab('compare')}
              id="tab-compare"
            >
              Compare ({compareIds.length})
            </button>
          </div>

          {/* Rankings Tab */}
          {activeTab === 'rankings' && (
            <div className="glass-card fade-in">
              <h2 className="dash-section-title">Candidate Rankings</h2>
              <div className="ranking-list">
                {rankings.map((r) => (
                  <div key={r.id} className="ranking-item">
                    <div className="ranking-medal">{getMedalIcon(r.rank)}</div>
                    <div className="ranking-info">
                      <div className="ranking-name">{r.name}</div>
                      <div className="ranking-email">{r.email || '—'}</div>
                    </div>
                    <div className="ranking-scores">
                      <div className="ranking-score-item">
                        <span className="ranking-score-label">Tech</span>
                        <span className={`ranking-score-val ${getScoreColor(r.technical_skill || 0)}`}>
                          {(r.technical_skill || 0).toFixed(1)}
                        </span>
                      </div>
                      <div className="ranking-score-item">
                        <span className="ranking-score-label">Comm</span>
                        <span className={`ranking-score-val ${getScoreColor(r.communication || 0)}`}>
                          {(r.communication || 0).toFixed(1)}
                        </span>
                      </div>
                      <div className="ranking-score-item">
                        <span className="ranking-score-label">PS</span>
                        <span className={`ranking-score-val ${getScoreColor(r.problem_solving || 0)}`}>
                          {(r.problem_solving || 0).toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <div className={`ranking-overall ${getScoreColor(r.overall_score || 0)}`}>
                      {(r.overall_score || 0).toFixed(1)}
                    </div>
                    <div className="ranking-actions">
                      <button className="action-btn view-btn" onClick={() => onViewCandidate(r.id)} title="View Details">View</button>
                      <button className="action-btn pdf-btn" onClick={() => handleDownloadPdf(r.id, r.name)} title="Download PDF">PDF</button>
                      <button className="action-btn del-btn" onClick={() => handleDelete(r.id)} title="Delete">Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Candidates Tab */}
          {activeTab === 'all' && (
            <div className="glass-card fade-in">
              <h2 className="dash-section-title">All Candidates</h2>
              <div className="candidates-grid">
                {candidates.map((c) => (
                  <div key={c.id} className="candidate-card">
                    <div className="candidate-card-header">
                      <div className="candidate-avatar">
                        {c.name ? c.name.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div className="candidate-card-info">
                        <div className="candidate-card-name">{c.name}</div>
                        <div className="candidate-card-email">{c.email || 'No email'}</div>
                      </div>
                      <div className="candidate-card-compare">
                        <label className="compare-checkbox">
                          <input
                            type="checkbox"
                            checked={compareIds.includes(c.id)}
                            onChange={() => toggleCompare(c.id)}
                          />
                          <span className="compare-label">Compare</span>
                        </label>
                      </div>
                    </div>
                    <div className="candidate-card-scores">
                      <div className="candidate-score-row">
                        <span>Overall</span>
                        <span className={getScoreColor(c.overall_score || 0)}>
                          {(c.overall_score || 0).toFixed(1)}/10
                        </span>
                      </div>
                      <div className="candidate-card-bar">
                        <div
                          className={`candidate-bar-fill ${getScoreColor(c.overall_score || 0)}`}
                          style={{ width: `${((c.overall_score || 0) / 10) * 100}%` }}
                        ></div>
                      </div>
                      <div className="candidate-score-mini-grid">
                        <div>
                          <span className="mini-label">Resume</span>
                          <span className={`mini-value ${getScoreColor(c.resume_score || 0)}`}>
                            {(c.resume_score || 0).toFixed(1)}
                          </span>
                        </div>
                        <div>
                          <span className="mini-label">Interview</span>
                          <span className={`mini-value ${getScoreColor(c.interview_score || 0)}`}>
                            {(c.interview_score || 0).toFixed(1)}
                          </span>
                        </div>
                        <div>
                          <span className="mini-label">GitHub</span>
                          <span className={`mini-value ${getScoreColor(c.github_score || 0)}`}>
                            {(c.github_score || 0).toFixed(1)}
                          </span>
                        </div>
                        <div>
                          <span className="mini-label">Video</span>
                          <span className={`mini-value ${getScoreColor(c.video_score || 0)}`}>
                            {(c.video_score || 0).toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="candidate-card-actions">
                      <button className="card-action-btn" onClick={() => onViewCandidate(c.id)}>
                        View Details
                      </button>
                      <button className="card-action-btn pdf" onClick={() => handleDownloadPdf(c.id, c.name)}>
                        PDF
                      </button>
                      <button className="card-action-btn danger" onClick={() => handleDelete(c.id)}>
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Compare Tab */}
          {activeTab === 'compare' && (
            <div className="glass-card fade-in">
              <h2 className="dash-section-title">Compare Candidates</h2>
              {compareIds.length < 2 ? (
                <div className="compare-hint">
                  <p>Select at least 2 candidates from the "All Candidates" tab to compare.</p>
                  <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
                    Use the checkboxes next to each candidate card.
                  </p>
                </div>
              ) : (
                <div className="compare-table-wrapper">
                  <table className="compare-table">
                    <thead>
                      <tr>
                        <th>Metric</th>
                        {compareData.map((c) => (
                          <th key={c.id}>{c.name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { label: 'Overall Score', key: 'overall_score' },
                        { label: 'Technical Skill', key: 'technical_skill' },
                        { label: 'Communication', key: 'communication' },
                        { label: 'Problem Solving', key: 'problem_solving' },
                        { label: 'Resume', key: 'resume_score' },
                        { label: 'Interview', key: 'interview_score' },
                        { label: 'GitHub', key: 'github_score' },
                        { label: 'Video', key: 'video_score' },
                      ].map((metric) => {
                        const scores = compareData.map(c => c[metric.key] || 0);
                        const maxScore = Math.max(...scores);
                        return (
                          <tr key={metric.key}>
                            <td className="compare-metric-label">{metric.label}</td>
                            {compareData.map((c, idx) => {
                              const val = c[metric.key] || 0;
                              const isHighest = val === maxScore && val > 0;
                              return (
                                <td key={c.id} className={`compare-cell ${isHighest ? 'highest' : ''}`}>
                                  <span className={getScoreColor(val)}>
                                    {val.toFixed(1)}
                                  </span>
                                  {isHighest && <span className="crown"></span>}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default RecruiterDashboard;
