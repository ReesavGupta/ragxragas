import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import SecretStr
from anyio.to_thread import run_sync
from dotenv import load_dotenv

load_dotenv()
FEWSHOT_PROMPT = """
Classify the following financial query as either 'real_time' or 'historical'.

Examples:
Q: What is the current stock price of Apple?
A: real_time

Q: What was Google's net income in 2018?
A: historical

Q: Show me the latest quarterly earnings for Tesla.
A: real_time

Q: What was Microsoft’s revenue in Q1 2021?
A: historical

Q: {query}
A:
"""

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY in environment.")
groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
llm = ChatGroq(api_key=SecretStr(groq_api_key), model=groq_model)
prompt = ChatPromptTemplate.from_template(FEWSHOT_PROMPT)

async def detect_query_type_llm(query: str) -> str:
    full_prompt = prompt.format(query=query)
    # langchain_groq is not async, so run in thread executor
    result = await run_sync(llm.invoke, full_prompt)
    answer = str(result).strip().lower()
    if "real_time" in answer:
        return "real_time"
    if "historical" in answer:
        return "historical"
    # Default fallback
    return "real_time" 