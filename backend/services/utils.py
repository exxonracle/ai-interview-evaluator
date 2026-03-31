import re

def extract_json(text: str):
    """Robustly extract JSON object from LLM response."""
    # Attempt to find JSON within markdown code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Attempt to find the first occurrence of { and the last occurrence of }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end+1]
    
    return text
