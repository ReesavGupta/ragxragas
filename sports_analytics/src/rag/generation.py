"""
Main RAG generation pipeline for sports analytics.
"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.retrievers import BaseRetriever
from pydantic import SecretStr

from .decomposition import QueryDecomposer
from .retrieval import SportsRetrievalSystem
from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class SportsRAGPipeline:
    """Complete RAG pipeline for sports analytics with query decomposition and advanced retrieval."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._init_llm()
        self.decomposer = QueryDecomposer()
        self.retrieval_system = SportsRetrievalSystem()
        self.prompt_template = self._init_prompt_template()
        
        logger.info("Sports RAG pipeline initialized")
    
    def _init_llm(self) -> ChatGroq:
        """Initialize Groq LLM."""
        if not self.settings:
            raise ValueError("Settings not available")
        
        return ChatGroq(
            api_key=SecretStr(self.settings.groq_api_key) if self.settings.groq_api_key else None,
            model=self.settings.groq_model,
            temperature=self.settings.temperature
        )
    
    def _init_prompt_template(self) -> PromptTemplate:
        """Initialize the response generation prompt template."""
        template = """
You are a sports analytics expert. Answer the question based on the provided context. Be specific, accurate, and provide relevant statistics when available.

Context:
{context}

Question: {question}

Instructions:
1. Use only the information provided in the context
2. Be specific and provide exact numbers/statistics when available
3. If the context doesn't contain enough information, say so
4. Focus on sports analytics and data-driven insights
5. Provide a clear, concise answer

Answer:
"""
        
        return PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )
    
    def answer_subquestion(self, sub_question: str) -> Dict[str, Any]:
        """Answer a single sub-question using RAG with RetrievalQA."""
        try:
            # Reduced rate limiting delay
            time.sleep(0.3)  # 0.3 second delay between requests
            
            # Retrieve and compress context
            compressed_docs = self.retrieval_system.retrieve_with_compression(sub_question)
            
            if not compressed_docs:
                logger.warning(f"No documents retrieved for query: {sub_question}")
                return {
                    "question": sub_question,
                    "answer": "I don't have enough information to answer this question.",
                    "sources": [],
                    "confidence": 0.0,
                    "document_count": 0
                }
            
            # Rerank documents
            reranked_docs = self.retrieval_system.rerank_documents(sub_question, compressed_docs)
            
            if not reranked_docs:
                logger.warning(f"No documents after reranking for query: {sub_question}")
                return {
                    "question": sub_question,
                    "answer": "I don't have enough information to answer this question.",
                    "sources": [],
                    "confidence": 0.0,
                    "document_count": 0
                }
            
            # Create a simple retriever class for reranked documents
            class SimpleRetriever(BaseRetriever):
                def __init__(self, docs):
                    super().__init__()
                    self._docs = docs
                
                def _get_relevant_documents(self, query):
                    return self._docs
            
            # Generate answer with citations using RetrievalQA
            rag_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=SimpleRetriever(reranked_docs),
                return_source_documents=True,
                chain_type="stuff"
            )
            
            # Run the chain with rate limiting protection
            try:
                result = rag_chain.invoke({"query": sub_question})
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    logger.warning(f"Rate limit hit, waiting 5 seconds before retry: {e}")
                    time.sleep(5)
                    result = rag_chain.invoke({"query": sub_question})
                else:
                    logger.error(f"Error in RetrievalQA chain: {e}")
                    # Return a fallback answer
                    return {
                        "question": sub_question,
                        "answer": f"Error processing question: {str(e)}",
                        "sources": [],
                        "confidence": 0.0,
                        "error": str(e),
                        "document_count": len(reranked_docs)
                    }
            
            # Extract answer and sources
            answer = result.get("result", str(result))
            source_docs = result.get("source_documents", [])
            
            # Prepare sources
            sources = []
            for doc in source_docs:
                source = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "file_type": doc.metadata.get("file_type", "unknown")
                }
                sources.append(source)
            
            # Calculate confidence based on document relevance
            confidence = min(1.0, len(reranked_docs) / 5.0)  # Simple heuristic
            
            return {
                "question": sub_question,
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "document_count": len(reranked_docs)
            }
            
        except Exception as e:
            logger.error(f"Error answering sub-question '{sub_question}': {e}")
            return {
                "question": sub_question,
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _answer_subquestions_parallel(self, sub_questions: List[str]) -> List[Dict[str, Any]]:
        """Answer sub-questions in parallel using ThreadPoolExecutor."""
        sub_answers = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=min(4, len(sub_questions))) as executor:
            # Submit all sub-questions for parallel processing
            future_to_question = {
                executor.submit(self.answer_subquestion, question): question 
                for question in sub_questions
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_question):
                try:
                    result = future.result()
                    sub_answers.append(result)
                except Exception as e:
                    question = future_to_question[future]
                    logger.error(f"Error processing sub-question '{question}': {e}")
                    # Add error result
                    sub_answers.append({
                        "question": question,
                        "answer": f"Error processing question: {str(e)}",
                        "sources": [],
                        "confidence": 0.0,
                        "error": str(e)
                    })
        
        # Sort results to maintain original order
        sub_answers.sort(key=lambda x: sub_questions.index(x["question"]))
        return sub_answers
    
    def answer_complex_query(self, query: str) -> Dict[str, Any]:
        """Answer a complex query by decomposing and answering sub-questions."""
        try:
            # Step 1: Decompose the query
            sub_questions = self.decomposer.decompose_query(query)
            
            # Step 2: Answer each sub-question in parallel
            sub_answers = self._answer_subquestions_parallel(sub_questions)
            
            # Step 3: Create aggregated response (simplified approach)
            aggregated_answer = self._aggregate_answers(query, sub_answers)
            
            # Step 4: Prepare response
            response = {
                "original_query": query,
                "final_answer": aggregated_answer,
                "sub_questions": sub_questions,
                "sub_answers": sub_answers,
                "overall_confidence": self._calculate_overall_confidence(sub_answers),
                "total_sources": self._count_total_sources(sub_answers)
            }
            
            logger.info(f"Completed complex query processing for: {query}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing complex query '{query}': {e}")
            return {
                "original_query": query,
                "final_answer": f"Error processing query: {str(e)}",
                "sub_questions": [],
                "sub_answers": [],
                "overall_confidence": 0.0,
                "error": str(e)
            }
    
    def _aggregate_answers(self, original_query: str, sub_answers: List[Dict[str, Any]]) -> str:
        """Aggregate sub-answers into a coherent final answer (simplified approach)."""
        try:
            # Simple aggregation: combine all answers
            aggregated = f"Based on the analysis of your question '{original_query}':\n\n"
            
            for i, sub_answer in enumerate(sub_answers, 1):
                aggregated += f"**Q:** {sub_answer['question']}\n**A:** {sub_answer['answer']}\n\n"
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error aggregating answers: {e}")
            # Fallback: concatenate sub-answers
            fallback = f"Based on the analysis:\n\n"
            for sub_answer in sub_answers:
                fallback += f"• {sub_answer['answer']}\n\n"
            return fallback
    
    def _calculate_overall_confidence(self, sub_answers: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence based on sub-answers."""
        if not sub_answers:
            return 0.0
        
        confidences = [answer.get("confidence", 0.0) for answer in sub_answers]
        return sum(confidences) / len(confidences)
    
    def _count_total_sources(self, sub_answers: List[Dict[str, Any]]) -> int:
        """Count total unique sources across all sub-answers."""
        all_sources = set()
        for sub_answer in sub_answers:
            sources = sub_answer.get("sources", [])
            for source in sources:
                source_key = source.get("source", "unknown")
                all_sources.add(source_key)
        
        return len(all_sources)
    
    def get_pipeline_stats(self, query: str) -> Dict[str, Any]:
        """Get comprehensive statistics about the RAG pipeline."""
        try:
            # Test decomposition
            decomp_stats = self.decomposer.get_decomposition_stats(query)
            
            # Test retrieval
            retrieval_stats = self.retrieval_system.get_retrieval_stats(query)
            
            # Test full pipeline
            pipeline_result = self.answer_complex_query(query)
            
            stats = {
                "query": query,
                "decomposition_stats": decomp_stats,
                "retrieval_stats": retrieval_stats,
                "pipeline_result": {
                    "sub_question_count": len(pipeline_result.get("sub_questions", [])),
                    "overall_confidence": pipeline_result.get("overall_confidence", 0.0),
                    "total_sources": pipeline_result.get("total_sources", 0),
                    "has_error": "error" in pipeline_result
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {e}")
            return {"error": str(e)} 