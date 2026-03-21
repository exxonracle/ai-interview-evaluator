from fastapi import FastAPI, UploadFile, File
import shutil
import os
from services.scoring import generate_final_score
from fastapi.middleware.cors import CORSMiddleware

from services.speech_to_text import transcribe_audio
from services.nlp_analysis import analyze_text
from services.speech_features import extract_speech_features

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = transcribe_audio(file_path)

    nlp_result = analyze_text(text)

    speech_result = extract_speech_features(file_path, text)

    os.remove(file_path)

    final_result = generate_final_score(nlp_result, speech_result)

    return {
        "transcription": text,
        "nlp_analysis": nlp_result,
        "speech_analysis": speech_result,
        "final_evaluation": final_result
    }