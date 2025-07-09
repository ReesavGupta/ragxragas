import os
from langchain_pinecone import PineconeVectorStore
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
from langchain import hub
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
from typing import Dict, TypedDict

# If your IDE cannot resolve this import, ensure 'langchain_nomic' is installed in your environment.
from langchain_nomic import NomicEmbeddings  # type: ignore

class IntentRAGPipeline:
    """
    RAG pipeline for a specific intent, using its own Pinecone index, embedding model, and prompt template.
    """
    def __init__(self, intent: str, index_name: str, prompt_template: str, llm):
        self.intent = intent
        self.index_name = index_name
        self.prompt_template = prompt_template
        self.llm = llm
        self.vector_store = self._init_vector_store()
        self.prompt = hub.pull(prompt_template) if prompt_template.startswith("rlm/") else prompt_template
        self.graph = self._build_graph()

    def _init_vector_store(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("Missing PINECONE_API_KEY in environment.")
        pc = Pinecone(api_key=api_key)
        index = pc.Index(self.index_name)
        nomic_api_key = os.getenv("NOMIC_API_KEY")
        embeddings = NomicEmbeddings(nomic_api_key=nomic_api_key, model="nomic-embed-text-v1.5")
        return PineconeVectorStore(embedding=embeddings, index=index)

    def _build_graph(self):
        def retrieve(state):
            docs = self.vector_store.similarity_search(state["question"], k=3)
            return {"context": docs}
        def generate(state):
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            # Ensure prompt is a string or has a callable 'invoke' method
            if hasattr(self.prompt, 'invoke') and callable(self.prompt.invoke):
                message = self.prompt.invoke({"question": state["question"], "context": docs_content})
            else:
                message = self.prompt.format(question=state["question"], context=docs_content)
            if hasattr(self.llm, 'invoke') and callable(self.llm.invoke):
                answer = self.llm.invoke(message)
            else:
                answer = message  # fallback for testing
            return {"answer": answer}
        class State(TypedDict):
            question: str
            context: list
            answer: str
        graph_builder = StateGraph(state_schema=State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        return graph_builder.compile()

    def run(self, question: str):
        state = {"question": question, "context": [], "answer": ""}  # type: ignore
        result = self.graph.invoke(state)  # type: ignore
        return result["answer"]

# Factory for all three intent pipelines
class IntentRAGFactory:
    """
    Factory to select the correct RAG pipeline by intent.
    """
    def __init__(self, llm):
        self.pipelines: Dict[str, IntentRAGPipeline] = {
            "technical_support": IntentRAGPipeline(
                intent="technical_support",
                index_name=os.getenv("PINECONE_INDEX_TECHNICAL_SUPPORT", "technical-support-index"),
                prompt_template=os.getenv("TECH_SUPPORT_PROMPT", "rlm/rag-prompt"),
                llm=llm
            ),
            "billing_account": IntentRAGPipeline(
                intent="billing_account",
                index_name=os.getenv("PINECONE_INDEX_BILLING_ACCOUNT", "billing-account-index"),
                prompt_template=os.getenv("BILLING_PROMPT", "rlm/rag-prompt"),
                llm=llm
            ),
            "feature_request": IntentRAGPipeline(
                intent="feature_request",
                index_name=os.getenv("PINECONE_INDEX_FEATURE_REQUEST", "feature-request-index"),
                prompt_template=os.getenv("FEATURE_PROMPT", "rlm/rag-prompt"),
                llm=llm
            ),
        }

    def get_pipeline(self, intent: str) -> IntentRAGPipeline:
        if intent not in self.pipelines:
            raise ValueError(f"No RAG pipeline for intent: {intent}")
        return self.pipelines[intent]

# Example usage (in FastAPI or other API layer):
# rag_factory = IntentRAGFactory(llm)
# rag_pipeline = rag_factory.get_pipeline(intent)
# answer = rag_pipeline.run(question) 