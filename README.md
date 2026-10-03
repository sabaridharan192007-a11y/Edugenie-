# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational assistant based on the project documentation supplied with this project. It provides:

- Question answering
- Beginner-friendly concept explanations
- 3-question multiple-choice quiz generation
- Educational text summarization
- Personalized learning paths

The supplied document describes a FastAPI backend, HTML/CSS frontend, Gemini-powered Q&A/quiz/summary/learning-path modules, and a lightweight explanation model. This implementation preserves the same modular architecture while using Google's current `google-genai` Python SDK. The explanation module defaults to Gemini-backed generation with an offline demo fallback. An optional local LaMini-Flan-T5-783M provider is also included to match the original document architecture; enable it with `EXPLANATION_PROVIDER=local` after installing `requirements-local.txt`. The model is downloaded on first use.

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── schemas.py
├── gemini_service.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── local_explanation.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── requirements-local.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_app.py
```

## Requirements

- Python 3.10 or newer
- Internet access for Gemini requests
- A Gemini API key for real AI generation

## VS Code setup — Windows

1. Extract/open the `EduGenie` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

5. Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

6. Install dependencies:

```powershell
pip install -r requirements.txt
```

7. Copy `.env.example` to `.env`.
8. Put your Gemini API key into `.env`:

```env
GEMINI_API_KEY=your_key_here
```

Never commit `.env` to Git. It is already included in `.gitignore`.

## Get a Gemini API key

Create/manage the key in Google AI Studio. Then put it in `.env`. Do not place the key in HTML, JavaScript, GitHub, or any public repository.

## Run the application

From the project folder with the virtual environment active:

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Test without an API key

The app automatically enters demo/offline mode when `GEMINI_API_KEY` is empty. This lets you verify the frontend, FastAPI routes, validation, and quiz UI without spending API quota.

## Run automated tests

```powershell
pip install -r requirements-dev.txt
pytest -q
```

Tests always run in offline mode, even if your `.env` contains a real key.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web interface |
| GET | `/health` | Application/API configuration check |
| POST | `/qa` | Answer a question |
| POST | `/explain` | Explain a topic simply |
| POST | `/quiz` | Generate 3 MCQs with 4 options each |
| POST | `/summarize` | Summarize educational text |
| POST | `/learn/recommendations` | Generate a beginner-to-advanced learning path |

Example request:

```json
{
  "text": "Explain the Pythagoras theorem with a simple example."
}
```

## Architecture

```text
Browser
  │
  ▼
HTML + CSS + JavaScript
  │  POST /qa, /explain, /quiz, /summarize, /learn/recommendations
  ▼
FastAPI (main.py)
  │
  ├── qna.py
  ├── explanation_module.py
  ├── quiz_module.py
  ├── summary_module.py
  └── learning_path.py
          │
          ▼
   gemini_service.py
          │
          ▼
      Google Gemini API
```

## Troubleshooting

### `ModuleNotFoundError`
Make sure the virtual environment is activated and run:

```powershell
pip install -r requirements.txt
```

### `Gemini API key is not configured`
Check that `.env` exists in the same folder as `main.py` and contains `GEMINI_API_KEY=...`.

### Gemini request fails
Check the API key, model name (`GEMINI_MODEL`, default `gemini-3.5-flash`; see Google's model list for current IDs), internet connection, and your Gemini API access/quota. You can change `GEMINI_MODEL` in `.env` to another model available to your account.

### Port 8000 is already in use
Run:

```powershell
uvicorn main:app --reload --port 8001
```

Then open `http://127.0.0.1:8001`.

### Optional: use the exact local LaMini explanation model

The supplied documentation names `LaMini-Flan-T5-783M` for concept explanation. The official model card identifies it as a 783M-parameter instruction-tuned T5 model and shows use through Hugging Face Transformers. urlLaMini-Flan-T5-783M model cardhttps://huggingface.co/MBZUAI/LaMini-Flan-T5-783M

Install the optional dependencies:

```powershell
pip install -r requirements-local.txt
```

Then set this in `.env`:

```env
EXPLANATION_PROVIDER=local
```

On the first explanation request, Hugging Face downloads the model weights. This is separate from the Gemini API and can require significant disk space/RAM.

## Changes in v1.1

- Added the missing `static/app.js` (safe Markdown rendering, interactive quiz with scoring, copy button, demo/live badge).
- Routes are now plain `def`, so slow Gemini calls no longer block the server.
- Friendly, non-leaking error messages; Gemini request timeout; one automatic retry for malformed quiz JSON.
- Quiz answers are validated to be one of the four options.
- Per-IP rate limit (`RATE_LIMIT_PER_MINUTE`) to protect your API quota.
- Higher output-token budget so thinking models don't return truncated/empty text.
- Default model updated to `gemini-3.5-flash`.

## Deployment

See [DEPLOY.md](DEPLOY.md). A `Dockerfile`, `Procfile` and `render.yaml` are included.
