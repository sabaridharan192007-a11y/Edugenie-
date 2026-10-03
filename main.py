import logging
import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import BASE_DIR, settings
from explanation_module import explain_topic
from gemini_service import AIServiceError
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from schemas import InputRequest
from summary_module import summarize_text

logger = logging.getLogger("edugenie")

app = FastAPI(
    title="EduGenie - AI Learning Assistant",
    description="A lightweight educational assistant powered by Google Gemini.",
    version="1.1.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- simple in-memory, per-IP rate limiter -------------------------------------------
_hits: dict = defaultdict(deque)
_hits_lock = threading.Lock()


def reset_rate_limiter() -> None:
    with _hits_lock:
        _hits.clear()


def rate_limit(request: Request) -> None:
    limit = settings.rate_limit_per_minute
    if limit <= 0:
        return
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _hits_lock:
        window = _hits[ip]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute and try again.")
        window.append(now)


# --- helpers ---------------------------------------------------------------------------
def _call(fn, *args):
    """Run a feature function and turn failures into safe HTTP errors."""
    try:
        return fn(*args)
    except AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unhandled error in %s", getattr(fn, "__name__", fn))
        raise HTTPException(
            status_code=500, detail="Something went wrong on the server. Please try again."
        ) from exc


# --- pages & health --------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"max_input_chars": settings.max_input_chars},
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "model": settings.gemini_model,
        "mode": "gemini" if settings.gemini_api_key else "demo/offline",
    }


# Plain `def` routes run in FastAPI's thread pool, so slow Gemini calls
# no longer block the event loop (and other users).
@app.post("/qa", dependencies=[Depends(rate_limit)])
def qa(payload: InputRequest):
    return {"result": _call(answer_question, payload.text)}


@app.post("/explain", dependencies=[Depends(rate_limit)])
def explain(payload: InputRequest):
    return {"result": _call(explain_topic, payload.text)}


@app.post("/quiz", dependencies=[Depends(rate_limit)])
def quiz(payload: InputRequest):
    return _call(generate_quiz, payload.text)


@app.post("/summarize", dependencies=[Depends(rate_limit)])
def summarize(payload: InputRequest):
    return {"result": _call(summarize_text, payload.text)}


@app.post("/learn/recommendations", dependencies=[Depends(rate_limit)])
def recommendations(payload: InputRequest):
    return {"result": _call(get_learning_recommendations, payload.text)}
