from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from difflib import SequenceMatcher

tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-base")

def clean_suggestion(suggestion: str) -> str:
    # Remove excessive repeated patterns like multiple .split("\n")
    if suggestion.count('.split') > 5:
        return ""
    # You can add more heuristics here if needed
    return suggestion.strip()

def correct_code(code: str, language: str):
    prefix = f"fix the following {language} code snippet with errors: "
    input_text = prefix + code.strip()

    inputs = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(
        inputs,
        max_length=1024,
        num_beams=5,
        early_stopping=True,
        no_repeat_ngram_size=3,      # Prevent repeating 3-gram sequences
        repetition_penalty=2.0,      # Penalize repetition strongly
        temperature=0.7,             # Lower randomness for focused output
    )
    suggestion = tokenizer.decode(outputs[0], skip_special_tokens=True)
    suggestion = clean_suggestion(suggestion)

    similarity = SequenceMatcher(None, code.strip(), suggestion).ratio()
    # Lower threshold to 0.9 so minor fixes are accepted
    if suggestion == "" or similarity > 0.9:
        return []

    return [{
        "line": 1,
        "message": "ML model suggests code improvement",
        "category": "ML Suggestion",
        "suggestion": suggestion
    }]
