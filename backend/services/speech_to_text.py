import whisper

model = whisper.load_model("small")


def transcribe_audio(file_path: str, resume_nouns: list = None):
    # Build context prompt, enriched with resume nouns if available
    prompt_context = "Interview context."
    if resume_nouns:
        noun_string = ", ".join(resume_nouns[:30])
        prompt_context += f" Key terms from candidate: {noun_string}."
    
    result = model.transcribe(
        file_path, 
        language="en", 
        fp16=False, 
        initial_prompt=prompt_context
    )
    return result["text"]