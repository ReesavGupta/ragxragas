from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio


def load_documents(doc_path: str):
    jq_schema = ".results[]" 
    loader = JSONLoader(
        file_path=doc_path,
        jq_schema=jq_schema,
        content_key=None,  
        text_content=False
    )
    pages = loader.load()
    return pages

def chunk_text(documents):
    splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splitted_texts = splitter.split_documents(documents)
    return splitted_texts

# if __name__ == "__main__":
#     json_file = "C:/Users/REESAV/Desktop/misogi-assignments/day-11[advance-RAG]/medical_ai_assistant/data/drug-event.json"
#     asyncio.run(load_documents(json_file))


