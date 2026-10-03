from typing import List

from pydantic import BaseModel, Field, model_validator

from gemini_service import generate_structured, get_client


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str

    @model_validator(mode="after")
    def correct_answer_must_be_an_option(self):
        wanted = self.correct_answer.strip().casefold()
        for option in self.options:
            if option.strip().casefold() == wanted:
                self.correct_answer = option  # normalise to the exact option text
                return self
        raise ValueError("correct_answer must match one of the options")


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(min_length=3, max_length=3)


def generate_quiz(content: str) -> dict:
    if not get_client():
        return {
            "questions": [
                {
                    "question": f"Which approach is most useful when studying {content[:60]}?",
                    "options": ["Understand the basics first", "Skip all examples", "Memorize without understanding", "Avoid practice"],
                    "correct_answer": "Understand the basics first",
                    "explanation": "Starting with fundamentals makes later concepts easier to understand.",
                },
                {
                    "question": "What is a good way to check understanding?",
                    "options": ["Explain the idea in your own words", "Never practice", "Only read the title", "Ignore mistakes"],
                    "correct_answer": "Explain the idea in your own words",
                    "explanation": "Explaining a concept is a simple way to test understanding.",
                },
                {
                    "question": "What should a learner do after finding a mistake?",
                    "options": ["Review and correct it", "Hide it", "Stop learning", "Repeat the same mistake"],
                    "correct_answer": "Review and correct it",
                    "explanation": "Mistakes are useful feedback when you review and correct them.",
                },
            ]
        }

    prompt = f"""Generate exactly 3 multiple-choice questions from the educational content below.
Each question must have exactly 4 plausible options and exactly one correct answer.
The correct_answer field must repeat one of the options word for word.
Return only data matching the requested schema. Include a short explanation for each answer.
Do not ask about information that is not present or reasonably implied by the content.

Content:
{content}
"""
    result = generate_structured(prompt, QuizResponse)
    return result.model_dump()
