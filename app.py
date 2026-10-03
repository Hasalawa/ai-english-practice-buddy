"""AI English Practice Buddy - Flask backend.

Flow: Frontend -> POST /check -> Flask -> Ollama -> Gemma -> JSON -> Frontend
"""
import json
import os

import requests
from flask import Flask, jsonify, request, send_from_directory

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
MAX_LEN = 500

app = Flask(__name__, static_folder="static", static_url_path="/static")

SYSTEM_PROMPT = """You are a friendly, patient English teacher helping a learner.
The learner will give you ONE sentence. Reply ONLY with a JSON object with these keys:
  "is_correct":  true or false (is the sentence already grammatically correct?)
  "corrected":   the corrected sentence (same as the input if already correct)
  "explanation": a short, simple explanation of the mistake in 1-2 sentences
                 (if already correct, say what is good about it)
  "example":     one new example sentence that uses the same grammar rule
  "better":      a more natural, fluent way to say the same thing
Use simple words. Do not add anything outside the JSON."""


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/check")
def check():
    data = request.get_json(silent=True) or {}
    sentence = (data.get("sentence") or "").strip()
    if not sentence:
        return jsonify(error="Please type a sentence first."), 400
    if len(sentence) > MAX_LEN:
        return jsonify(error=f"Please keep it under {MAX_LEN} characters."), 400

    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Sentence: {sentence}"},
        ],
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        content = r.json()["message"]["content"]
        result = json.loads(content)
    except requests.ConnectionError:
        return jsonify(error="Can't reach Ollama. Is it running? (ollama serve)"), 503
    except (requests.RequestException, KeyError, ValueError):
        return jsonify(error="The AI gave an unexpected answer. Please try again."), 502

    return jsonify(
        original=sentence,
        is_correct=bool(result.get("is_correct")),
        corrected=str(result.get("corrected", sentence)),
        explanation=str(result.get("explanation", "")),
        example=str(result.get("example", "")),
        better=str(result.get("better", "")),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
