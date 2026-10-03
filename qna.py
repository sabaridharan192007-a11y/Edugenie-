from gemini_service import generate_text, get_client


def answer_question(question: str) -> str:
    if not get_client():
        return (
            "Demo mode: Gemini is not configured. Add GEMINI_API_KEY to .env for an AI answer. "
            f"Your question was: {question}"
        )

    prompt = f"""You are EduGenie, a friendly educational assistant.
Answer the student's question accurately and concisely.
Use simple language, short paragraphs, and examples when helpful.
Do not invent facts. If the question is ambiguous, state the assumption.

Student question:
{question}
"""
    return generate_text(prompt)
