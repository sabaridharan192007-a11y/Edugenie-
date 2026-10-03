from gemini_service import generate_text, get_client


def get_learning_recommendations(topic: str) -> str:
    if not get_client():
        return (
            f"Demo learning path for {topic}:\n"
            "1. Beginner: learn definitions and basic vocabulary.\n"
            "2. Foundation: study core concepts with examples.\n"
            "3. Practice: solve simple exercises and mini-projects.\n"
            "4. Intermediate: learn common applications and problem-solving.\n"
            "5. Advanced: build a project and study advanced references.\n"
            "Configure Gemini for a personalized AI-generated path and resources."
        )

    prompt = f"""Create a personalized learning path for the topic: {topic}
Assume the learner is a beginner unless the topic itself implies otherwise.
Organize it from beginner to advanced. For each stage include:
- concepts to learn
- a realistic suggested timeline
- practice activity
- resource types (video, article, book, documentation)
Finish with a small project idea and a revision checklist.
Keep it practical and concise. Do not fabricate specific URLs.
"""
    return generate_text(prompt)
