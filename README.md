# AI Interview Evaluator

A beautiful, high-performance platform for evaluating interview candidates using AI. It analyze candidate speech, provides a communication score, screens resumes, and assess answer accuracy using the Groq Llama 3.3 model.

## ✨ Features

- **🗣️ Speech Analysis**: Evalutes pitch variation (tone), vocal projection (confidence), and words per minute (flow).
- **📝 Answer Accuracy**: Correlates the candidate's transcribed spoken answer with the intended interview question using a high-accuracy LLM.
- **📄 Resume Screening**: Scans PDF resumes for education, projects, skills, and experience, providing automated scoring.
- **🤖 AI Coaching**: Generates professional, encouraging feedback based on the candidate's holistic performance.
- **📊 Real-time Dashboard**: Color-coded scoring (Excellent, Good, Needs Improvement) with instant visual feedback.

---

## 🛠️ Tech Stack

- **Frontend**: React.js (modern glassmorphism UI)
- **Backend**: FastAPI (Python)
- **AI/LLM**: Groq (Llama 3.3-70b-versatile)
- **Speech Processing**: Whisper (Transciption), Librosa (Audio analysis)

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

## 💡 Usage Guide

1. **Enter Question**: Type the interview question or upload a PDF/DOCX file containing questions.
2. **Upload Audio**: Browse for an audio recording of the candidate's response.
3. **Upload Resume (Optional)**: Provide a PDF resume for screening.
4. **Analyze**: Click "Analyze Candidate" and view the comprehensive results on the dashboard.

## 🛡️ Privacy & Security
- API keys are stored locally in `.env` and are ignored by git.
- Temporary files are automatically deleted after processing.
