import os
from langchain_groq import ChatGroq
from pydantic.types import SecretStr

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

llm = ChatGroq(
    api_key=SecretStr(GROQ_API_KEY),
    model="llama3-70b-8192"
)

def generate_quiz(context: str, difficulty: str = "medium") :
    prompt = (
        f"Generate 5 {difficulty} questions with answers and explanations "
        f"based on the following educational content:\n{context}"
    )
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"Error generating quiz: {e}" 