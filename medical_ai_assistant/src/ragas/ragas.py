from medical_ai_assistant.src.vector_store.embeddings_and_vectorstore import initialize_vec_store_and_embedding_model
from medical_ai_assistant.src.retriever.retriever import build_rag_graph, init_groq
from medical_ai_assistant.src.ragas.test_data import expected_responses, sample_queries
from langchain import hub
from dotenv import load_dotenv

load_dotenv()
# initailize all the necessary objects
vector_store = initialize_vec_store_and_embedding_model()
rag_graph = build_rag_graph(vector_store)
llm = init_groq()
prompt = hub.pull("rlm/rag-prompt")


def get_most_relevant_docs(query):
    retrieved_docs = vector_store.similarity_search(query=query, k=3)
    return retrieved_docs

def generate_answer(query, docs):

    docs_content = "\n\n".join(doc.page_content for doc in docs)

    message = prompt.invoke({"question": query, "context": docs_content})
   
    answer = llm.invoke(message)
    return answer.content


golden_dataset = []
for query, reference in zip(sample_queries, expected_responses):
    relevant_docs = get_most_relevant_docs(query)
    response = generate_answer(query, relevant_docs)
    golden_dataset.append(
        {
            "user_input": query,
            "response": response,
            "retrieved_contexts": [doc.page_content for doc in relevant_docs],
            "reference": reference
        }
    )

from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness, ContextPrecision, AnswerRelevancy

# i was getting too many time out erors while evaluating need to set the timeout parameter in the RunConfig and ensure it is passed to the evaluation function. 
run_config = RunConfig(
    timeout=60,        # seconds per operation
    max_retries=3,     # fewer retries for dev
    max_wait=10,       # less wait between retries
    max_workers=8      # or 16, depending on your system/API
)

evaluation_dataset = EvaluationDataset.from_list(golden_dataset)
# usually for evaluation we should use a bigger llm but for this assignment im using the same llm to evaluate
evaluator_llm = LangchainLLMWrapper(llm)

result = evaluate(
    dataset=evaluation_dataset,
    metrics=[
        LLMContextRecall(),
        Faithfulness(),
        FactualCorrectness(),
        AnswerRelevancy(),
        ContextPrecision()
    ],
    llm=evaluator_llm,
    run_config=run_config
)

print(result)

