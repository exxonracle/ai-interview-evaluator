import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [resume, setResume] = useState(null);
  const [questionFile, setQuestionFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      if (question.trim()) {
        formData.append("question", question.trim());
      }
      if (resume) {
        formData.append("resume", resume);
      }
      if (questionFile) {
        formData.append("question_file", questionFile);
      }

      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Backend error. Check if server is running.");
    }

    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 8) return "excellent";
    if (score >= 5) return "good";
    return "needs-improvement";
  };

  return (
    <div className="app-container">
      <header>
        <h1 className="gradient-text">AI Interview Evaluator</h1>
        <p className="subtitle">AI-powered speech, fluency, and content analysis.</p>
      </header>

      <div className="glass-card upload-section">
        <input
          className="question-input"
          type="text"
          placeholder="Enter the interview question (optional)..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <label className="file-label">
          {questionFile ? `Questions: ${questionFile.name}` : "Or upload question file - PDF/DOCX (optional)..."}
          <input
            type="file"
            className="file-input"
            accept=".pdf,.docx,.doc"
            onChange={(e) => setQuestionFile(e.target.files[0])}
          />
        </label>

        <label className="file-label">
          {file ? `Audio: ${file.name}` : "Browse audio file..."}
          <input
            type="file"
            className="file-input"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </label>

        <label className="file-label">
          {resume ? `Resume: ${resume.name}` : "Upload resume PDF (optional)..."}
          <input
            type="file"
            className="file-input"
            accept=".pdf"
            onChange={(e) => setResume(e.target.files[0])}
          />
        </label>

        <button 
          className="analyze-button" 
          onClick={handleUpload} 
          disabled={loading || !file}
        >
          {loading ? (
            <><span className="spinner"></span> Processing AI Analysis...</>
          ) : (
            "Analyze Candidate"
          )}
        </button>
      </div>

      {result && (
        <div className="glass-card fade-in">
          <h2 style={{marginTop: 0, marginBottom: '20px', color: '#f8fafc'}}>Evaluation Dashboard</h2>
          
          <div className="results-grid">
            <div className="metric-card">
              <div className="metric-title">Score</div>
              <div className={`metric-value ${getScoreColor(result.final_evaluation.final_score)}`}>
                {result.final_evaluation.final_score.toFixed(1)}<span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
              </div>
              <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                {result.final_evaluation.performance}
              </div>
            </div>

            <div className="metric-card" style={{borderColor: 'rgba(168, 85, 247, 0.3)'}}>
              <div className="metric-title">Vocal Tone</div>
              <div className={`metric-value ${getScoreColor(result.speech_analysis.tone_score || 0)}`}>
                {result.speech_analysis.tone_score ? result.speech_analysis.tone_score.toFixed(1) : "0.0"}
                <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
              </div>
              <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                Pitch Variation Score
              </div>
            </div>

            <div className="metric-card" style={{borderColor: 'rgba(56, 189, 248, 0.3)'}}>
              <div className="metric-title">Confidence</div>
              <div className={`metric-value ${getScoreColor(result.speech_analysis.confidence_score || 0)}`}>
                {result.speech_analysis.confidence_score ? result.speech_analysis.confidence_score.toFixed(1) : "0.0"}
                <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
              </div>
              <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                Vocal Projection Score
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Speech Flow</div>
              <div className={`metric-value ${getScoreColor(result.speech_analysis.flow_score || 0)}`}>
                {result.speech_analysis.flow_score ? result.speech_analysis.flow_score.toFixed(1) : "0.0"}
                <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
              </div>
              <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                Pacing & Pauses [{result.speech_analysis.words_per_minute} WPM]
              </div>
            </div>

            <div className="metric-card" style={{borderColor: 'rgba(251, 191, 36, 0.3)'}}>
              <div className="metric-title">Clarity</div>
              <div className={`metric-value ${getScoreColor(result.speech_analysis.clarity_score || 0)}`}>
                {result.speech_analysis.clarity_score ? result.speech_analysis.clarity_score.toFixed(1) : "0.0"}
                <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
              </div>
              <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                Pronunciation & Pacing
              </div>
            </div>

            {result.final_evaluation.answer_accuracy !== null && result.final_evaluation.answer_accuracy !== undefined && (
              <div className="metric-card" style={{borderColor: 'rgba(244, 114, 182, 0.3)'}}>
                <div className="metric-title">Answer Accuracy</div>
                <div className={`metric-value ${getScoreColor(result.final_evaluation.answer_accuracy)}`}>
                  {result.final_evaluation.answer_accuracy.toFixed(1)}
                  <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                </div>
                <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                  Relevance to Question
                </div>
              </div>
            )}
          </div>

          {result.final_evaluation.answer_accuracy_feedback && (
            <div className="feedback-section" style={{marginTop: '20px', borderLeft: '3px solid #f472b6'}}>
              <h3>Answer Accuracy</h3>
              <div className="feedback-text">
                <p style={{margin: 0}}>{result.final_evaluation.answer_accuracy_feedback}</p>
              </div>
            </div>
          )}

          <div className="feedback-section" style={{marginTop: '20px'}}>
            <h3>Feedback</h3>
            <div className="feedback-text">
              {result.final_evaluation.feedback.map((f, i) => (
                <p key={i} style={{margin: 0}}>{f}</p>
              ))}
            </div>
          </div>

          <div className="feedback-section" style={{marginTop: '20px'}}>
            <h3>Audio Transcription</h3>
            <div className="transcription-box">
              "{result.transcription}"
            </div>
          </div>

          {result.final_evaluation.resume_sections && (
            <div className="glass-card fade-in" style={{marginTop: '24px'}}>
              <h2 style={{marginTop: 0, marginBottom: '20px', color: '#f8fafc'}}>Resume Analysis</h2>

              {result.final_evaluation.resume_breakdown && (
                <div className="results-grid" style={{marginBottom: '24px'}}>
                  {result.final_evaluation.resume_score !== null && (
                    <div className="metric-card" style={{borderColor: 'rgba(129, 140, 248, 0.3)'}}>
                      <div className="metric-title">Resume Score</div>
                      <div className={`metric-value ${getScoreColor(result.final_evaluation.resume_score)}`}>
                        {result.final_evaluation.resume_score.toFixed(1)}
                        <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                      </div>
                      <div style={{color: '#94a3b8', fontSize: '0.85rem', marginTop: '5px'}}>
                        Overall Weighted Score
                      </div>
                    </div>
                  )}
                  <div className="metric-card" style={{borderColor: 'rgba(96, 165, 250, 0.3)'}}>
                    <div className="metric-title">Experience</div>
                    <div className={`metric-value ${getScoreColor(result.final_evaluation.resume_breakdown.experience_score)}`}>
                      {result.final_evaluation.resume_breakdown.experience_score.toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                  </div>
                  <div className="metric-card" style={{borderColor: 'rgba(168, 85, 247, 0.3)'}}>
                    <div className="metric-title">Projects</div>
                    <div className={`metric-value ${getScoreColor(result.final_evaluation.resume_breakdown.projects_score)}`}>
                      {result.final_evaluation.resume_breakdown.projects_score.toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                  </div>
                  <div className="metric-card" style={{borderColor: 'rgba(251, 191, 36, 0.3)'}}>
                    <div className="metric-title">Education</div>
                    <div className={`metric-value ${getScoreColor(result.final_evaluation.resume_breakdown.education_score)}`}>
                      {result.final_evaluation.resume_breakdown.education_score.toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                  </div>
                  <div className="metric-card" style={{borderColor: 'rgba(52, 211, 153, 0.3)'}}>
                    <div className="metric-title">Skills</div>
                    <div className={`metric-value ${getScoreColor(result.final_evaluation.resume_breakdown.skills_score)}`}>
                      {result.final_evaluation.resume_breakdown.skills_score.toFixed(1)}
                      <span style={{fontSize: '1rem', color: '#64748b'}}>/10</span>
                    </div>
                  </div>
                </div>
              )}

              <ResumeAccordion title="Education" content={result.final_evaluation.resume_sections.education} />
              <ResumeAccordion title="Experience" content={result.final_evaluation.resume_sections.experience} />
              <ResumeAccordion title="Projects" content={result.final_evaluation.resume_sections.projects} />
              <ResumeAccordion title="Skills" content={result.final_evaluation.resume_sections.skills} />
            </div>
          )}

          {result.final_evaluation.resume_feedback && (
            <div className="feedback-section" style={{marginTop: '20px', borderLeft: '3px solid #60a5fa'}}>
              <h3>Resume Assessment</h3>
              <div className="feedback-text">
                <p style={{margin: 0}}>{result.final_evaluation.resume_feedback}</p>
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}

function ResumeAccordion({ title, content }) {
  const [open, setOpen] = React.useState(false);
  const items = content ? content.split('\n').filter(line => line.trim()) : [content];
  const isList = items.length > 1;
  return (
    <div className="accordion-item">
      <button className="accordion-header" onClick={() => setOpen(!open)}>
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

export default App;
