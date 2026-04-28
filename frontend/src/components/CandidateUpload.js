import React, { useState } from 'react';

function CandidateUpload({ onViewCandidate }) {
  const [candidateName, setCandidateName] = useState('');
  const [candidateEmail, setCandidateEmail] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [interviewFile, setInterviewFile] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [questionFile, setQuestionFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!candidateName.trim()) {
      setError('Candidate name is required.');
      return;
    }
    if (!resumeFile && !interviewFile && !videoFile && !githubUrl.trim()) {
      setError('Please provide at least one evaluation input (resume, interview audio, video, or GitHub URL).');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setLoadingStage('Uploading files...');

    try {
      const formData = new FormData();
      formData.append('candidate_name', candidateName.trim());
      if (candidateEmail.trim()) formData.append('candidate_email', candidateEmail.trim());
      if (githubUrl.trim()) formData.append('github_repo_url', githubUrl.trim());
      if (question.trim()) formData.append('question', question.trim());
      if (resumeFile) formData.append('resume', resumeFile);
      if (interviewFile) formData.append('interview_audio', interviewFile);
      if (videoFile) formData.append('video_file', videoFile);
      if (questionFile) formData.append('question_file', questionFile);
      if (jdFile) formData.append('jd_file', jdFile);

      setLoadingStage('AI is analyzing candidate...');

      const response = await fetch('http://127.0.0.1:8000/evaluate-candidate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to evaluate candidate. Check if backend is running.');
    }

    setLoading(false);
    setLoadingStage('');
  };

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

  const clearFile = (setter) => {
    setter(null);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="gradient-text">AI Candidate Evaluator</h1>
        <p className="subtitle">
          Upload files for comprehensive AI-powered skill assessment — audio and video are auto-transcribed
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card upload-form">
        {/* Candidate Info */}
        <div className="form-section-label">Candidate Information</div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="candidate_name" className="form-label">
              Name <span className="required">*</span>
            </label>
            <input
              id="candidate_name"
              type="text"
              className="form-input"
              placeholder="Enter full name..."
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="candidate_email" className="form-label">Email</label>
            <input
              id="candidate_email"
              type="email"
              className="form-input"
              placeholder="candidate@email.com"
              value={candidateEmail}
              onChange={(e) => setCandidateEmail(e.target.value)}
            />
          </div>
        </div>

        {/* File Uploads */}
        <div className="form-section-label">Evaluation Inputs</div>

        {/* Resume Upload */}
        <div className="form-group">
          <label className="form-label">
            <span className="form-label-icon"></span> Resume PDF
            <span className="form-hint">PDF, auto-extracted — 30% weight</span>
          </label>
          <div className="file-upload-row">
            <label className="file-label">
              {resumeFile ? `✓ ${resumeFile.name}` : 'Choose resume PDF...'}
              <input
                type="file"
                className="file-input"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files[0])}
              />
            </label>
            {resumeFile && (
              <button type="button" className="clear-btn" onClick={() => clearFile(setResumeFile)}>✕</button>
            )}
          </div>
        </div>

        {/* Interview Audio Upload */}
        <div className="form-group">
          <label className="form-label">
            <span className="form-label-icon"></span> Interview Audio
            <span className="form-hint">Audio file, auto-transcribed via Whisper — 30% weight</span>
          </label>
          <div className="file-upload-row">
            <label className="file-label">
              {interviewFile ? `✓ ${interviewFile.name}` : 'Choose interview audio file...'}
              <input
                type="file"
                className="file-input"
                accept="audio/*,.mp3,.wav,.m4a,.ogg,.flac,.webm"
                onChange={(e) => setInterviewFile(e.target.files[0])}
              />
            </label>
            {interviewFile && (
              <button type="button" className="clear-btn" onClick={() => clearFile(setInterviewFile)}>✕</button>
            )}
          </div>
        </div>

        {/* GitHub URL or Profile */}
        <div className="form-group">
          <label htmlFor="github_url" className="form-label">
            <span className="form-label-icon"></span> GitHub Repo or Profile
            <span className="form-hint">Repo URL or username for portfolio analysis — 20% weight</span>
          </label>
          <input
            id="github_url"
            type="text"
            className="form-input"
            placeholder="https://github.com/username/repo  or  username"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
          />
        </div>

        {/* Video Upload */}
        <div className="form-group">
          <label className="form-label">
            <span className="form-label-icon"></span> Project Demo / Video
            <span className="form-hint">Video file with visual + audio analysis — 20% weight</span>
          </label>
          <div className="file-upload-row">
            <label className="file-label">
              {videoFile ? `✓ ${videoFile.name}` : 'Choose video file...'}
              <input
                type="file"
                className="file-input"
                accept="video/*,audio/*,.mp4,.avi,.mov,.mkv,.webm,.mp3,.wav,.m4a"
                onChange={(e) => setVideoFile(e.target.files[0])}
              />
            </label>
            {videoFile && (
              <button type="button" className="clear-btn" onClick={() => clearFile(setVideoFile)}>✕</button>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="form-section-label" style={{marginTop: '10px'}}>Job Description (for Role-Fit Scoring)</div>
        <div className="form-group">
          <label className="form-label">
            <span className="form-label-icon"></span> JD File
            <span className="form-hint">Upload PDF/DOCX/TXT — used for JD matching & GitHub repo selection</span>
          </label>
          <div className="file-upload-row">
            <label className="file-label">
              {jdFile ? `✓ ${jdFile.name}` : 'Choose JD file...'}
              <input type="file" className="file-input" accept=".pdf,.docx,.doc,.txt" onChange={(e) => setJdFile(e.target.files[0])} />
            </label>
            {jdFile && <button type="button" className="clear-btn" onClick={() => clearFile(setJdFile)}>✕</button>}
          </div>
        </div>
        {/* Interview Question */}
        <div className="form-section-label" style={{marginTop: '10px'}}>Interview Question</div>
        <div className="form-group">
          <label className="form-label">
            Question Text
            <span className="form-hint">For answer accuracy scoring — type or upload a file</span>
          </label>
          <input type="text" className="form-input" placeholder="Enter interview question (optional)..." value={question} onChange={(e) => setQuestion(e.target.value)} />
        </div>
        <div className="form-group">
          <div className="file-upload-row">
            <label className="file-label small-label">
              {questionFile ? `✓ ${questionFile.name}` : 'Or upload question file (PDF/DOCX)...'}
              <input type="file" className="file-input" accept=".pdf,.docx,.doc" onChange={(e) => setQuestionFile(e.target.files[0])} />
            </label>
            {questionFile && <button type="button" className="clear-btn" onClick={() => clearFile(setQuestionFile)}>✕</button>}
          </div>
        </div>

        {error && (
          <div className="error-banner">
            <span></span> {error}
          </div>
        )}

        <button
          type="submit"
          className="analyze-button"
          disabled={loading || !candidateName.trim()}
          id="evaluate-submit-btn"
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              <span>Analyzing Candidate...</span>
            </>
          ) : (
            <>
              <span></span>
              <span>Evaluate Candidate</span>
            </>
          )}
        </button>
      </form>

      {/* Loading Progress */}
      {loading && (
        <div className="glass-card progress-card">
          <div className="progress-header">
            <span className="progress-icon pulse"></span>
            <span>{loadingStage}</span>
          </div>
          <div className="progress-modules">
            {[
              { icon: '', label: 'Resume', active: !!resumeFile },
              { icon: '', label: 'Interview', active: !!interviewFile },
              { icon: '', label: 'GitHub', active: !!githubUrl.trim() },
              { icon: '', label: 'Video', active: !!videoFile },
            ].map((mod, i) => (
              <div key={i} className={`progress-module-item ${mod.active ? 'active-module' : 'inactive-module'}`}>
                <span className={mod.active ? 'shimmer' : ''}>{mod.icon} {mod.label}</span>
              </div>
            ))}
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill"></div>
          </div>
          <p className="progress-note">
            {interviewFile || videoFile ? '⏳ Transcription may take a moment...' : ''}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="glass-card fade-in result-card">
          <div className="result-header">
            <h2>Evaluation Complete</h2>
            <span className="result-candidate-name">{result.candidate_name}</span>
          </div>

          {/* Overall Scores */}
          <div className="scores-grid">
            <div className="score-card overall-card">
              <div className="score-card-label">Overall Score</div>
              <div className={`score-card-value ${getScoreColor(result.scores.overall_score)}`}>
                {result.scores.overall_score.toFixed(1)}
              </div>
              <div className="score-card-badge">{getScoreLabel(result.scores.overall_score)}</div>
            </div>
            <div className="score-card">
              <div className="score-card-label">Technical Skill</div>
              <div className={`score-card-value ${getScoreColor(result.scores.technical_skill)}`}>
                {result.scores.technical_skill.toFixed(1)}
              </div>
              <div className="score-card-sub">/10</div>
            </div>
            <div className="score-card">
              <div className="score-card-label">Communication</div>
              <div className={`score-card-value ${getScoreColor(result.scores.communication)}`}>
                {result.scores.communication.toFixed(1)}
              </div>
              <div className="score-card-sub">/10</div>
            </div>
            <div className="score-card">
              <div className="score-card-label">Problem Solving</div>
              <div className={`score-card-value ${getScoreColor(result.scores.problem_solving)}`}>
                {result.scores.problem_solving.toFixed(1)}
              </div>
              <div className="score-card-sub">/10</div>
            </div>
          </div>

          {/* Module Breakdown */}
          <div className="module-breakdown">
            <h3>Module Breakdown</h3>
            <div className="module-grid">
              {[
                { key: 'resume', label: 'Resume', icon: '', score: result.scores.resume_score, weight: '30%', detail: result.module_details?.resume },
                { key: 'interview', label: 'Interview', icon: '', score: result.scores.interview_score, weight: '30%', detail: result.module_details?.interview },
                { key: 'github', label: 'GitHub', icon: '', score: result.scores.github_score, weight: '20%', detail: result.module_details?.github },
                { key: 'video', label: 'Video', icon: '', score: result.scores.video_score, weight: '20%', detail: result.module_details?.video },
              ].map((mod) => (
                <div key={mod.key} className="module-card">
                  <div className="module-card-header">
                    <span className="module-icon">{mod.icon}</span>
                    <span className="module-label">{mod.label}</span>
                    <span className="module-weight">{mod.weight}</span>
                  </div>
                  <div className={`module-score ${getScoreColor(mod.score)}`}>
                    {mod.score.toFixed(1)}<span>/10</span>
                  </div>
                  {mod.detail?.explanation && (
                    <p className="module-explanation">{mod.detail.explanation}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* JD Match Results */}
          {result.jd_match && (
            <div className="jd-match-section">
              <h3>Job Description Match</h3>
              <div className="jd-match-header">
                <div className={`jd-fit-badge ${result.jd_match.recommendation?.includes('STRONG') ? 'strong' : result.jd_match.recommendation?.includes('GOOD') ? 'good-fit' : result.jd_match.recommendation?.includes('MODERATE') ? 'moderate' : 'weak'}`}>
                  {result.jd_match.recommendation}
                </div>
                <div className={`jd-fit-score ${getScoreColor(result.jd_match.overall_fit_score || 0)}`}>
                  {(result.jd_match.overall_fit_score || 0).toFixed(1)}<span>/10</span>
                </div>
              </div>
              {result.jd_requirements?.role_title && (
                <div className="jd-role-title">Role: {result.jd_requirements.role_title}</div>
              )}
              <p className="module-explanation">{result.jd_match.explanation}</p>
              <div className="jd-scores-row">
                <div className="jd-score-item"><span>Skills Match</span><span className={getScoreColor(result.jd_match.skills_match_score||0)}>{(result.jd_match.skills_match_score||0).toFixed(1)}</span></div>
                <div className="jd-score-item"><span>Experience</span><span className={getScoreColor(result.jd_match.experience_match_score||0)}>{(result.jd_match.experience_match_score||0).toFixed(1)}</span></div>
                <div className="jd-score-item"><span>Domain Fit</span><span className={getScoreColor(result.jd_match.domain_relevance_score||0)}>{(result.jd_match.domain_relevance_score||0).toFixed(1)}</span></div>
              </div>
              {result.jd_match.matched_skills?.length > 0 && (
                <div className="jd-skills"><strong>Matched:</strong> {result.jd_match.matched_skills.join(', ')}</div>
              )}
              {result.jd_match.missing_skills?.length > 0 && (
                <div className="jd-skills missing"><strong>Missing:</strong> {result.jd_match.missing_skills.join(', ')}</div>
              )}
              {result.jd_match.strengths_for_role?.length > 0 && (
                <div className="jd-list"><strong>Strengths:</strong><ul>{result.jd_match.strengths_for_role.map((s,i) => <li key={i}>{s}</li>)}</ul></div>
              )}
              {result.jd_match.concerns_for_role?.length > 0 && (
                <div className="jd-list concerns"><strong>Concerns:</strong><ul>{result.jd_match.concerns_for_role.map((s,i) => <li key={i}>{s}</li>)}</ul></div>
              )}
            </div>
          )}

          {/* Portfolio Info (if GitHub account mode) */}
          {result.module_details?.github?.mode === 'portfolio' && result.module_details.github.portfolio_info && (
            <div className="portfolio-section">
              <h3>GitHub Portfolio: {result.module_details.github.portfolio_info.display_name}</h3>
              <div className="portfolio-stats">
                <div className="portfolio-stat"><span className="stat-value">{result.module_details.github.portfolio_info.total_repos}</span><span className="stat-label">Repos</span></div>
                <div className="portfolio-stat"><span className="stat-value">{result.module_details.github.portfolio_info.total_stars}</span><span className="stat-label">Stars</span></div>
                <div className="portfolio-stat"><span className="stat-value">{result.module_details.github.portfolio_info.followers}</span><span className="stat-label">Followers</span></div>
              </div>
              {result.module_details.github.portfolio_info.all_languages && (
                <div className="portfolio-langs">
                  <strong>Languages:</strong> {Object.entries(result.module_details.github.portfolio_info.all_languages).sort((a,b)=>b[1]-a[1]).slice(0,8).map(([l,c])=>`${l} (${c})`).join(', ')}
                </div>
              )}
              {result.module_details.github.analyzed_repos?.length > 0 && (
                <div className="analyzed-repos">
                  <strong>Analyzed Projects:</strong>
                  {result.module_details.github.analyzed_repos.map((r,i) => (
                    <div key={i} className="analyzed-repo-item">
                      <span className="repo-name">{r.repo_name}</span>
                      <span className="repo-stars">Stars: {r.stars||0}</span>
                      <span className={`repo-score ${getScoreColor((parseFloat(r.code_quality||0)+parseFloat(r.complexity||0))/2)}`}>
                        Quality: {r.code_quality} | Complexity: {r.complexity}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Speech Analysis (from interview audio) */}
          {result.speech_analysis && (
            <div className="speech-section">
              <h3>Speech & Fluency Analysis</h3>
              <div className="results-grid">
                {[
                  { label: 'Vocal Tone', value: result.speech_analysis.tone_score, sub: 'Pitch Variation' },
                  { label: 'Confidence', value: result.speech_analysis.confidence_score, sub: 'Vocal Projection' },
                  { label: 'Speech Flow', value: result.speech_analysis.flow_score, sub: `${result.speech_analysis.words_per_minute} WPM` },
                  { label: 'Clarity', value: result.speech_analysis.clarity_score, sub: 'Pronunciation & Pacing' },
                ].map((item) => (
                  <div key={item.label} className="metric-card">
                    <div className="metric-title">{item.label}</div>
                    <div className={`metric-value ${getScoreColor(item.value || 0)}`}>
                      {(item.value || 0).toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                    <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                      {item.sub}
                    </div>
                  </div>
                ))}
              </div>
              {result.speech_score && (
                <div className="speech-overall">
                  <span>ML Speech Score: </span>
                  <span className={getScoreColor(result.speech_score.final_score)}>
                    {result.speech_score.final_score.toFixed(1)}/10
                  </span>
                  <span className="speech-level"> — {result.speech_score.performance}</span>
                </div>
              )}
            </div>
          )}

          {/* Video Demo Visual Analysis */}
          {result.video_demo && result.video_demo.visual_analysis && result.video_demo.visual_analysis.visual_quality > 0 && (
            <div className="video-demo-section">
              <h3>Project Demo Analysis</h3>
              <div className="demo-score-header">
                <span>Demo Score: </span>
                <span className={getScoreColor(result.video_demo.demo_score || 0)}>
                  {(result.video_demo.demo_score || 0).toFixed(1)}/10
                </span>
              </div>
              <p className="module-explanation">{result.video_demo.demo_explanation}</p>
              <div className="results-grid">
                {[
                  { label: 'Visual Quality', value: result.video_demo.visual_analysis.visual_quality },
                  { label: 'Demo Depth', value: result.video_demo.visual_analysis.demo_depth },
                  { label: 'UI Complexity', value: result.video_demo.visual_analysis.ui_complexity },
                ].map((item) => (
                  <div key={item.label} className="metric-card">
                    <div className="metric-title">{item.label}</div>
                    <div className={`metric-value ${getScoreColor(item.value || 0)}`}>
                      {(item.value || 0).toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                  </div>
                ))}
              </div>
              {result.video_demo.visual_analysis.code_visible && (
                <div className="demo-badge">Code Detected on Screen</div>
              )}
              {result.video_demo.visual_analysis.technologies_detected?.length > 0 && (
                <div className="demo-techs">
                  <strong>Technologies Detected:</strong> {result.video_demo.visual_analysis.technologies_detected.join(', ')}
                </div>
              )}
              {result.video_demo.visual_analysis.screen_content_summary && (
                <div className="demo-summary">
                  <strong>Screen Content:</strong> {result.video_demo.visual_analysis.screen_content_summary}
                </div>
              )}
            </div>
          )}

          {/* Answer Accuracy */}
          {result.answer_accuracy && (
            <div className="feedback-section" style={{marginTop: '20px', borderLeft: '3px solid #f472b6'}}>
              <h3>Answer Accuracy: <span className={getScoreColor(result.answer_accuracy.score)}>{result.answer_accuracy.score.toFixed(1)}/10</span></h3>
              <div className="feedback-text">
                <p style={{margin: 0}}>{result.answer_accuracy.feedback}</p>
              </div>
            </div>
          )}

          {/* LLM Feedback */}
          {result.llm_feedback && (
            <div className="feedback-section" style={{marginTop: '20px'}}>
              <h3>AI Coaching Feedback</h3>
              <div className="feedback-text">
                <p style={{margin: 0}}>{result.llm_feedback}</p>
              </div>
            </div>
          )}

          {/* Resume Screening Details */}
          {result.resume_screening && result.resume_screening.sections && (
            <div className="feedback-section" style={{marginTop: '20px', borderLeft: '3px solid #60a5fa'}}>
              <h3>Resume Breakdown
                {result.resume_screening.score > 0 && (
                  <span className={`resume-score-inline ${getScoreColor(result.resume_screening.score)}`}>
                    {' '}{result.resume_screening.score.toFixed(1)}/10
                  </span>
                )}
              </h3>
              {result.resume_screening.feedback && (
                <div className="feedback-text" style={{marginBottom: '12px'}}>
                  <p style={{margin: 0}}>{result.resume_screening.feedback}</p>
                </div>
              )}
              <ResumeAccordion title="Education" content={result.resume_screening.sections.education} />
              <ResumeAccordion title="Experience" content={result.resume_screening.sections.experience} />
              <ResumeAccordion title="Projects" content={result.resume_screening.sections.projects} />
              <ResumeAccordion title="Skills" content={result.resume_screening.sections.skills} />
            </div>
          )}

          {/* Transcriptions */}
          {result.interview_transcript && (
            <div className="feedback-section" style={{marginTop: '20px'}}>
              <h3>Interview Transcription</h3>
              <div className="transcription-box">
                "{result.interview_transcript}"
              </div>
            </div>
          )}

          {result.video_transcript && (
            <div className="feedback-section" style={{marginTop: '20px'}}>
              <h3>Video Transcription</h3>
              <div className="transcription-box">
                "{result.video_transcript}"
              </div>
            </div>
          )}

          {/* Score Explanations */}
          {result.explanations && (
            <div className="explanations-section">
              <h3>AI Score Explanations</h3>
              {result.explanations.overall_explanation && (
                <div className="explanation-item overall-explanation">
                  <p style={{margin: 0}}>{result.explanations.overall_explanation}</p>
                </div>
              )}
              {[
                { key: 'technical_skill_explanation', label: 'Technical Skill' },
                { key: 'communication_explanation', label: 'Communication' },
                { key: 'problem_solving_explanation', label: 'Problem Solving' },
              ].map((item) => (
                result.explanations[item.key] && (
                  <div key={item.key} className="explanation-item">
                    <strong>{item.label}:</strong> {result.explanations[item.key]}
                  </div>
                )
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ResumeAccordion({ title, content }) {
  const [open, setOpen] = useState(false);
  const items = content ? content.split('\n').filter(line => line.trim()) : [content];
  const isList = items.length > 1;
  return (
    <div className="accordion-item">
      <button type="button" className="accordion-header" onClick={() => setOpen(!open)}>
        <span>{title}</span>
        <span className={`accordion-arrow ${open ? 'open' : ''}`}>▸</span>
      </button>
      {open && (
        <div className="accordion-body">
          {isList ? (
            <ul style={{margin: 0, paddingLeft: '20px', color: '#cbd5e1', lineHeight: '1.8'}}>
              {items.map((item, i) => (
                <li key={i} style={{marginBottom: '6px'}}>{item.replace(/^[-•]\s*/, '')}</li>
              ))}
            </ul>
          ) : (
            <p style={{margin: 0, color: '#cbd5e1', lineHeight: '1.6'}}>{content}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default CandidateUpload;
