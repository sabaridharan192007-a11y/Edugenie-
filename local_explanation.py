"""Optional local LaMini-Flan-T5 explanation provider.

Install requirements-local.txt before selecting EXPLANATION_PROVIDER=local.
The model weights are downloaded by Hugging Face on first use.
"""

import threading

from gemini_service import AIServiceError

MODEL_NAME = "MBZUAI/LaMini-Flan-T5-783M"
# T5 handles roughly 512 input tokens; keep the topic short enough to fit.
MAX_TOPIC_CHARS = 1200

_pipe = None
_lock = threading.Lock()


def _get_pipeline():
    global _pipe
    with _lock:
        if _pipe is None:
            try:
                from transformers import pipeline
            except ImportError as exc:
                raise AIServiceError(
                    "Local explanation requires transformers/torch. Install requirements-local.txt."
                ) from exc
            _pipe = pipeline("text2text-generation", model=MODEL_NAME)
    return _pipe


def explain_with_lamini(topic: str) -> str:
    pipe = _get_pipeline()
    topic = topic[:MAX_TOPIC_CHARS]
    prompt = (
        "Explain this educational topic for a beginner. Use simple language, one example, "
        "and two key points. Topic: " + topic
    )
    with _lock:  # the model is not safe to call from several threads at once
        result = pipe(prompt, max_new_tokens=220, do_sample=False)
    return result[0]["generated_text"].strip()
