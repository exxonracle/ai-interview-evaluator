# AI Candidate Evaluator: Multi-Signal AI Hiring Platform

A professional, high-performance platform for evaluating candidates across multiple technical dimensions. It leverages the Groq Llama 3.3 model to provide an objective, data-driven assessment of Resumes, Interviews, GitHub Portfolios, and Project Demos.

## ✨ Features

### Interview Evaluator (Original)
- **🗣️ Speech Analysis**: Evalutes pitch variation (tone), vocal projection (confidence), and words per minute (flow).
- **📝 Answer Accuracy**: Correlates the candidate's transcribed spoken answer with the intended interview question using a high-accuracy LLM.
- **📄 Resume Screening**: Scans PDF resumes for education, projects, skills, and experience, providing automated scoring.
- **🤖 AI Coaching**: Generates professional, encouraging feedback based on the candidate's holistic performance.
- **📊 Real-time Dashboard**: Color-coded scoring (Excellent, Good, Needs Improvement) with instant visual feedback.

### Skill-Based Hiring Platform (New)
- **🧠 Multi-Signal Evaluation**: Evaluate candidates across 4 dimensions — Resume, Interview, GitHub, Video
- **📄 Resume Analyzer**: LLM-powered scoring of skills, experience, education, and projects
- **🎤 Interview Evaluator**: Scores communication, correctness, and problem-solving from transcripts
- **🐙 GitHub Analyzer**: Fetches repo data via GitHub API and evaluates code quality, tech stack, and complexity
- **🎬 Video Evaluator**: Analyzes video transcripts for clarity, confidence, and structured thinking
- **⚖️ Weighted Scoring Engine**: Resume (30%), Interview (30%), GitHub (20%), Video (20%)
- **📊 Recruiter Dashboard**: Rankings, candidate comparison, score cards
- **📥 PDF Reports**: Downloadable evaluation reports for each candidate
- **💾 Database**: Persistent storage of candidate evaluations using SQLite
- **💡 AI Explanations**: LLM-generated explanations for every composite score

---

## 🛠️ Tech Stack

- **Frontend**: React.js (modern glassmorphism UI)
- **Backend**: FastAPI (Python)
- **AI/LLM**: Groq (Llama 3.3-70b-versatile)
- **Speech Processing**: Whisper (Transciption), Librosa (Audio analysis)
- **Database**: SQLite (aiosqlite)
- **PDF Generation**: ReportLab
- **HTTP Client**: httpx (async GitHub API calls)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.14+
- Node.js & npm
- A [Groq API Key](https://console.groq.com/keys)

### 2. Backend Setup
Navigate to the backend folder and set up your environment:

```bash
cd backend
# Create and activate virtual environment (if not done)
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend/` folder:
```env
GROQ_API_KEY=your_key_here
GITHUB_TOKEN=your_github_token_here  # Optional, for higher API rate limits
```

**Run Server:**
```bash
# From the backend/ folder
uvicorn main:app --reload
```

### 3. Frontend Setup
Navigate to the frontend folder and start the React app:

```bash
cd ../frontend
npm install
npm start
```

The application will be available at `http://localhost:3000`.

---

## 📡 API Endpoints

### Original
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Audio-based interview analysis |

### Hiring Platform
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/evaluate-candidate` | Full multi-signal AI evaluation |
| `GET` | `/candidates` | List all evaluated candidates |
| `GET` | `/candidates/{id}` | Detailed evaluation report |
| `GET` | `/rankings` | Candidates ranked by overall score |
| `GET` | `/candidates/{id}/report` | Download PDF evaluation report |
| `DELETE` | `/candidates/{id}` | Remove candidate and data |

---

## 💡 Usage Guide

### Interview Evaluator
1. **Enter Question**: Type the interview question or upload a PDF/DOCX file containing questions.
2. **Upload Audio**: Browse for an audio recording of the candidate's response.
3. **Upload Resume (Optional)**: Provide a PDF resume for screening.
4. **Analyze**: Click "Analyze Candidate" and view the comprehensive results on the dashboard.

### Skill-Based Hiring Platform
1. **Navigate to "Candidate Upload"** using the top navigation bar.
2. **Fill in candidate details**: Name, email, resume text, interview transcript, GitHub URL, video transcript.
3. **Click "Evaluate Candidate"** — the AI analyzes all 4 dimensions simultaneously.
4. **View Results**: Scores, module breakdowns, and AI explanations appear instantly.
5. **Recruiter Dashboard**: See all candidates ranked, compare side-by-side, and download PDF reports.

## 🛡️ Privacy & Security
- API keys are stored locally in `.env` and are ignored by git.
- Temporary files are automatically deleted after processing.
- Candidate data is stored locally in SQLite (no external database).
