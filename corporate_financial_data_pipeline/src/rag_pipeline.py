import os
from langchain_pinecone import PineconeVectorStore
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import SecretStr

class RAGPipeline:
    def __init__(self, vector_store=None):
        if vector_store is not None:
            self.vector_store = vector_store
        else:
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            pinecone_index = os.getenv("PINECONE_INDEX_NAME")
            nomic_api_key = os.getenv("NOMIC_API_KEY")
            if not (pinecone_api_key and pinecone_index and nomic_api_key):
                raise ValueError("Missing one or more required environment variables for RAG pipeline.")
            pc = Pinecone(api_key=pinecone_api_key)
            index = pc.Index(pinecone_index)
            self.vector_store = PineconeVectorStore(
                embedding=NomicEmbeddings(nomic_api_key=nomic_api_key, model="nomic-embed-text-v1.5"),
                index=index
            )
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in environment.")
        groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        self.llm = ChatGroq(api_key=SecretStr(groq_api_key), model=groq_model)
        self.prompt = ChatPromptTemplate.from_template(
            """You are a financial data assistant. Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"""
        )

    async def run(self, question: str, k: int = 3):
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = self.prompt.format(context=context, question=question)
        from anyio.to_thread import run_sync
        answer = await run_sync(self.llm.invoke, prompt)
        return {"answer": str(answer), "context": [doc.page_content for doc in docs]} 