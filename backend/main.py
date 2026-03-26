from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import shutil
import os
from services.scoring import generate_final_score
from fastapi.middleware.cors import CORSMiddleware

from services.speech_to_text import transcribe_audio
from services.nlp_analysis import analyze_text
from services.speech_features import extract_speech_features
from services.llm_feedback import generate_audio_feedback
from services.answer_accuracy import evaluate_answer_accuracy
from services.resume_screening import extract_resume_text, extract_key_nouns, screen_resume

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_question_from_file(file_path: str) -> str:
    """Extract question text from a PDF or DOCX file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    elif ext in (".docx", ".doc"):
        from docx import Document
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    else:
        return ""


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), 
    question: Optional[str] = Form(None),
    question_file: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None)
):

    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract question from uploaded file if provided
    question_text = question.strip() if question and question.strip() else None
    if not question_text and question_file and question_file.filename:
        qf_path = f"temp_{question_file.filename}"
        with open(qf_path, "wb") as buffer:
            shutil.copyfileobj(question_file.file, buffer)
        question_text = extract_question_from_file(qf_path)
        os.remove(qf_path)

    # Extract resume nouns for Whisper priming if resume is provided
    resume_nouns = None
    resume_text = None
    resume_path = None
    if resume and resume.filename:
        resume_path = f"temp_{resume.filename}"
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        resume_text = extract_resume_text(resume_path)
        resume_nouns = extract_key_nouns(resume_text)

    text = transcribe_audio(file_path, resume_nouns)

    nlp_result = analyze_text(text)

    speech_result = extract_speech_features(file_path, text)

    os.remove(file_path)

    final_result = generate_final_score(nlp_result, speech_result)

    llm_feedback_text = await generate_audio_feedback(nlp_result, speech_result, final_result, text)
    final_result["feedback"] = [llm_feedback_text]

    accuracy_result = await evaluate_answer_accuracy(question_text, text)
    if accuracy_result:
        final_result["answer_accuracy"] = accuracy_result["score"]
        final_result["answer_accuracy_feedback"] = accuracy_result["feedback"]
    else:
        final_result["answer_accuracy"] = None
        final_result["answer_accuracy_feedback"] = None

    # Resume screening
    if resume_text:
        resume_result = await screen_resume(resume_text)
        final_result["resume_score"] = resume_result["score"]
        final_result["resume_sections"] = resume_result.get("sections")
        final_result["resume_breakdown"] = resume_result.get("breakdown")
        final_result["resume_feedback"] = resume_result.get("feedback")
        os.remove(resume_path)
    else:
        final_result["resume_score"] = None
        final_result["resume_sections"] = None
        final_result["resume_breakdown"] = None
        final_result["resume_feedback"] = None

    return {
        "transcription": text,
        "nlp_analysis": nlp_result,
        "speech_analysis": speech_result,
        "final_evaluation": final_result
    }