import os
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

class State(TypedDict):
    question: str
    context : List[Document]
    answer : str
    
def init_groq():
    llm = init_chat_model("llama3-8b-8192", model_provider="groq") 
    return llm

def build_rag_graph(vector_store):
    prompt = hub.pull("rlm/rag-prompt", )
    llm = init_groq()
        
    def retrieve(state: State):        
        retrieved_docs  = vector_store.similarity_search(state["question"], k=3)
        return {"context" : retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"]) 
        message = prompt.invoke({"question": state["question"], "context": docs_content})

        answer = llm.invoke(message)
        return {"answer": answer.content}
    
    # Finally, we compile our application into a single graph object. In this case, we are just connecting the retrieval and generation steps into a single sequence.
    graph_builder = StateGraph(state_schema=State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    return graph