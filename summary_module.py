from gemini_service import generate_text, get_client


def summarize_text(text: str) -> str:
    if not get_client():
        words = text.split()
        sample = " ".join(words[:60])
        suffix = "..." if len(words) > 60 else ""
        return f"Demo summary: {sample}{suffix}"

    prompt = f"""Summarize the educational passage below for quick revision.
Keep the important facts and meaning. Use simple language and bullet points when useful.
Do not add information that is not present in the passage.

Passage:
{text}
"""
    return generate_text(prompt)
