import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import SecretStr

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    llm = ChatOpenAI(api_key=SecretStr(OPENAI_API_KEY), model="gpt-3.5-turbo")

ARTICLE_PROMPT = """
You are an expert blog writer. Write a detailed Medium-style article based on the following idea:

Title: {title}
Summary: {summary}
Tags: {tags}

Structure the article with:
- Introduction
- Main sections (with headings)
- Conclusion
- Use markdown formatting
- Be clear, engaging, and informative
"""

def generate_article(title, summary, tags):
    prompt = ChatPromptTemplate.from_template(ARTICLE_PROMPT)
    chain = prompt | llm
    result = chain.invoke({
        "title": title,
        "summary": summary,
        "tags": ', '.join(tags) if isinstance(tags, list) else tags
    })
    return result.content if hasattr(result, 'content') else str(result) 