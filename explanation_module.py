from config import settings
from gemini_service import generate_text, get_client


def explain_topic(topic: str) -> str:
    if settings.explanation_provider.lower() == "local":
        from local_explanation import explain_with_lamini

        return explain_with_lamini(topic)

    if not get_client():
        return (
            "Demo mode explanation: "
            f"{topic} is a concept that should be understood by starting with its definition, "
            "main idea, a simple example, and then a practical use. Configure Gemini for a full AI explanation."
        )

    prompt = f"""Explain the following educational topic for a beginner.
Start with a one-sentence definition, then explain the main idea in simple language,
follow with a small example, and finish with 2 key points to remember.
Avoid unnecessary jargon.

Topic: {topic}
"""
    return generate_text(prompt)
