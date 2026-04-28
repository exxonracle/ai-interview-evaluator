import React, { useState, useEffect } from 'react';

function CandidateDetail({ candidateId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(`http://127.0.0.1:8000/candidates/${candidateId}`);
        const detail = await resp.json();
        if (detail.error) {
          setError(detail.error);
        } else {
          setData(detail);
        }
      } catch (err) {
        setError('Failed to load candidate details.');
      }
      setLoading(false);
    };
    fetchDetail();
  }, [candidateId]);

  const getScoreColor = (score) => {
    if (score >= 8) return 'excellent';
    if (score >= 5) return 'good';
    return 'needs-improvement';
  };

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Excellent';
    if (score >= 5) return 'Good';
    return 'Needs Improvement';
  };

  const handleDownloadPdf = () => {
    const url = `http://127.0.0.1:8000/candidates/${candidateId}/report`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `evaluation_report_${(data?.name || 'candidate').replace(/\s/g, '_')}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px' }}>
          <span className="spinner" style={{ width: '40px', height: '40px' }}></span>
          <p style={{ color: '#94a3b8', marginTop: '20px' }}>Loading candidate profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="glass-card error-banner">
          <p>{error}</p>
          <button onClick={onBack} className="analyze-button" style={{ maxWidth: '200px', marginTop: '15px' }}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const report = data?.full_report || {};
  const explanations = report.explanations || {};
  const moduleDetails = report.module_details || {};

  return (
    <div className="page-container">
      <button onClick={onBack} className="back-button" id="back-to-dashboard">
        Back to Dashboard
      </button>

      {/* Candidate Header */}
      <div className="glass-card detail-header">
        <div className="detail-avatar">
          {data.name ? data.name.charAt(0).toUpperCase() : '?'}
        </div>
        <div className="detail-info">
          <h1 className="detail-name">{data.name}</h1>
          <p className="detail-email">{data.email || 'No email provided'}</p>
          <p className="detail-date">Evaluated: {data.evaluation_date ? new Date(data.evaluation_date).toLocaleDateString() : 'N/A'}</p>
        </div>
        <button className="pdf-download-button" onClick={handleDownloadPdf} id="download-report-btn">
          Download PDF Report
        </button>
      </div>

      {/* Overall Score Hero */}
      <div className="glass-card detail-hero">
        <div className="hero-overall">
          <div className="hero-label">Overall Score</div>
          <div className={`hero-score ${getScoreColor(data.overall_score || 0)}`}>
            {(data.overall_score || 0).toFixed(1)}
          </div>
          <div className="hero-badge">{getScoreLabel(data.overall_score || 0)}</div>
        </div>
        <div className="hero-composites">
          {[
            { label: 'Technical Skill', value: data.technical_skill || 0 },
            { label: 'Communication', value: data.communication || 0 },
            { label: 'Problem Solving', value: data.problem_solving || 0 },
          ].map((item) => (
            <div key={item.label} className="hero-composite-item">
              <div className="hero-composite-label">{item.label}</div>
              <div className={`hero-composite-value ${getScoreColor(item.value)}`}>
                {item.value.toFixed(1)}
              </div>
              <div className="hero-composite-bar">
                <div
                  className={`hero-bar-fill ${getScoreColor(item.value)}`}
                  style={{ width: `${(item.value / 10) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Radar Chart (CSS) */}
      <div className="glass-card">
        <h2 className="detail-section-title">Skills Radar</h2>
        <div className="radar-container">
          <div className="radar-chart">
            {[
              { label: 'Resume', value: data.resume_score || 0, angle: 0 },
              { label: 'Interview', value: data.interview_score || 0, angle: 90 },
              { label: 'GitHub', value: data.github_score || 0, angle: 180 },
              { label: 'Video', value: data.video_score || 0, angle: 270 },
            ].map((item) => {
              const radius = (item.value / 10) * 100;
              const radians = (item.angle - 90) * (Math.PI / 180);
              const x = 50 + radius * Math.cos(radians) * 0.4;
              const y = 50 + radius * Math.sin(radians) * 0.4;
              return (
                <React.Fragment key={item.label}>
                  <div
                    className="radar-point"
                    style={{ left: `${x}%`, top: `${y}%` }}
                    title={`${item.label}: ${item.value.toFixed(1)}`}
                  >
                    <span className="radar-point-dot"></span>
                  </div>
                  <div
                    className={`radar-label radar-label-${item.angle}`}
                  >
                    <span className="radar-label-text">{item.label}</span>
                    <span className={`radar-label-score ${getScoreColor(item.value)}`}>
                      {item.value.toFixed(1)}
                    </span>
                  </div>
                </React.Fragment>
              );
            })}
            <div className="radar-ring radar-ring-outer"></div>
            <div className="radar-ring radar-ring-mid"></div>
            <div className="radar-ring radar-ring-inner"></div>
            <div className="radar-crosshair-h"></div>
            <div className="radar-crosshair-v"></div>
          </div>
        </div>
      </div>

      {/* Module Details */}
      <div className="glass-card">
        <h2 className="detail-section-title">Module Breakdown</h2>
        <div className="detail-modules-grid">
          {[
            { key: 'resume', label: 'Resume Analysis', icon: '', score: data.resume_score, weight: '30%', detail: moduleDetails.resume },
            { key: 'interview', label: 'Interview Evaluation', icon: '', score: data.interview_score, weight: '30%', detail: moduleDetails.interview },
            { key: 'github', label: 'GitHub Analysis', icon: '', score: data.github_score, weight: '20%', detail: moduleDetails.github },
            { key: 'video', label: 'Video Evaluation', icon: '', score: data.video_score, weight: '20%', detail: moduleDetails.video },
          ].map((mod) => (
            <div key={mod.key} className="detail-module-card">
              <div className="detail-module-header">
                <span className="detail-module-icon">{mod.icon}</span>
                <span className="detail-module-label">{mod.label}</span>
                <span className="detail-module-weight">{mod.weight}</span>
              </div>
              <div className={`detail-module-score ${getScoreColor(mod.score || 0)}`}>
                {(mod.score || 0).toFixed(1)}
                <span className="detail-module-score-sub">/10</span>
              </div>
              {mod.detail && (
                <div className="detail-module-breakdown">
                  {Object.entries(mod.detail).filter(([k, v]) => 
                    k !== 'explanation' && k !== 'repo_info' && typeof v === 'number'
                  ).map(([k, v]) => (
                    <div key={k} className="detail-sub-score">
                      <span className="detail-sub-label">{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                      <span className={`detail-sub-value ${getScoreColor(v)}`}>{v.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              )}
              {mod.detail?.explanation && (
                <p className="detail-module-explanation">{mod.detail.explanation}</p>
              )}
              {mod.detail?.repo_info && (
                <div className="detail-repo-info">
                  <span>Stars: {mod.detail.repo_info.stars || 0}</span>
                  <span className="detail-repo-name">{mod.detail.repo_info.name}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Score Explanations */}
      {(explanations.overall_explanation || explanations.technical_skill_explanation) && (
        <div className="glass-card">
          <h2 className="detail-section-title">AI Score Explanations</h2>
          {explanations.overall_explanation && (
            <div className="detail-explanation overall-explanation">
              <strong>Overall Assessment:</strong> {explanations.overall_explanation}
            </div>
          )}
          {[
            { key: 'technical_skill_explanation', label: 'Technical Skill' },
            { key: 'communication_explanation', label: 'Communication' },
            { key: 'problem_solving_explanation', label: 'Problem Solving' },
          ].map((item) => (
            explanations[item.key] ? (
              <div key={item.key} className="detail-explanation">
                <strong>{item.label}:</strong> {explanations[item.key]}
              </div>
            ) : null
          ))}
        </div>
      )}
    </div>
  );
}

export default CandidateDetail;
