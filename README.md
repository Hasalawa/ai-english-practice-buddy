# AI English Practice Buddy

![CI](https://github.com/YOUR_USERNAME/ai-english-practice-buddy/actions/workflows/ci.yml/badge.svg)

An AI-powered English practice tool built for my friend, who is improving their English.

## Features
- **Grammar check** – type a sentence, get the corrected version
- **Explain my mistake** – a short, simple explanation of why
- **Better version** – a more natural way to say it, plus an example sentence

## AI
Uses the open-weight **Gemma** model (`gemma3:1b`) running locally through **Ollama**.
Why open models? Sentences stay on your laptop (privacy), there is no API cost, and you can swap the model with one env var.

## Tech stack
HTML · CSS · JavaScript · Python (Flask) · Ollama · Gemma

## Run it
```bash
# 1. Install Ollama (https://ollama.com) and pull the model
ollama pull gemma3:1b

# 2. Install and start the app
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

Optional env vars: `OLLAMA_MODEL` (default `gemma3:1b`), `OLLAMA_URL`.

## How it works
```
Browser -> POST /check -> Flask -> Ollama -> Gemma -> JSON -> Browser
```

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```
GitHub Actions runs lint (ruff) and tests on every push and pull request. The AI call is mocked, so CI doesn't need Ollama.
