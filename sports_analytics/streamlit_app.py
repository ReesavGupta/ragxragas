#!/usr/bin/env python3
"""
Streamlit web app for Sports Analytics RAG System
"""

import streamlit as st
import sys
from pathlib import Path
import time
from typing import Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.rag.generation import SportsRAGPipeline
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Sports Analytics RAG System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #b3d9ff;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    .source-box {
        background-color: #f0f8ff;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border: 1px solid #cce5ff;
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #000000 !important;
    }
    .confidence-high { color: #28a745; }
    .confidence-medium { color: #ffc107; }
    .confidence-low { color: #dc3545; }
    
    /* Default text color for light theme */
    .stMarkdown, .stMarkdown p, .stMarkdown div,
    .stText, .stText p, .stText div {
        color: #000000 !important;
    }
    
    /* Dark theme text color */
    @media (prefers-color-scheme: dark) {
        .stMarkdown, .stMarkdown p, .stMarkdown div,
        .stText, .stText p, .stText div {
            color: #ffffff !important;
        }
    }
    
    /* Force white text in dark containers */
    [data-testid="stAppViewContainer"] .stMarkdown,
    [data-testid="stAppViewContainer"] .stMarkdown p,
    [data-testid="stAppViewContainer"] .stMarkdown div,
    [data-testid="stAppViewContainer"] .stText,
    [data-testid="stAppViewContainer"] .stText p,
    [data-testid="stAppViewContainer"] .stText div {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

def get_confidence_color(confidence: float) -> str:
    """Get color class based on confidence level."""
    if confidence >= 0.7:
        return "confidence-high"
    elif confidence >= 0.4:
        return "confidence-medium"
    else:
        return "confidence-low"

def display_metrics(response: Dict[str, Any]):
    """Display key metrics from the response."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Confidence",
            value=f"{response.get('overall_confidence', 0.0):.1%}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Sources",
            value=response.get('total_sources', 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Sub-questions",
            value=len(response.get('sub_questions', [])),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Processing Time",
            value=f"{response.get('processing_time', 0):.1f}s",
            delta=None
        )

def display_sub_questions(sub_questions: list):
    """Display sub-questions in an organized way."""
    st.markdown("### 🔍 Query Decomposition")
    for i, question in enumerate(sub_questions, 1):
        st.markdown(f"**{i}.** {question}")

def display_sub_answers(sub_answers: list):
    """Display sub-answers with their details."""
    st.markdown("### 📝 Sub-Answers")
    
    for i, answer in enumerate(sub_answers, 1):
        with st.expander(f"Sub-question {i}: {answer.get('question', 'N/A')[:50]}..."):
            # Answer
            st.markdown("**Answer:**")
            st.markdown(answer.get('answer', 'No answer available'))
            
            # Confidence
            confidence = answer.get('confidence', 0.0)
            confidence_color = get_confidence_color(confidence)
            st.markdown(f"**Confidence:** <span class='{confidence_color}'>{confidence:.1%}</span>", unsafe_allow_html=True)
            
            # Document count
            doc_count = answer.get('document_count', 0)
            st.markdown(f"**Documents retrieved:** {doc_count}")
            
            # Sources
            sources = answer.get('sources', [])
            if sources:
                st.markdown("**Sources:**")
                for j, source in enumerate(sources[:3], 1):  # Show first 3 sources
                    st.markdown(f"<div class='source-box'>{j}. {source.get('content', 'N/A')[:200]}...</div>", 
                               unsafe_allow_html=True)

def display_final_answer(final_answer: str):
    """Display the final aggregated answer."""
    st.markdown("### 🎯 Final Answer")
    st.markdown(f"<div class='answer-box'>{final_answer}</div>", unsafe_allow_html=True)

def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ Sports Analytics RAG System</h1>', unsafe_allow_html=True)
    st.markdown("### Advanced Retrieval-Augmented Generation for Sports Analytics")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Quick Queries")
        st.markdown("Try these example queries:")
        
        example_queries = [
            "What are the key performance metrics for Manchester City?",
            "How does Liverpool's defensive performance compare to other teams?",
            "What are the top scoring statistics in the league?",
            "Which players have the best assist records?",
            "How do goalkeeper statistics compare across teams?",
            "What are the most important metrics for evaluating midfielders?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.query = query
                st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # Advanced options
        with st.expander("Advanced Options"):
            st.checkbox("Show detailed logs", value=False, key="show_logs")
            st.checkbox("Show raw response", value=False, key="show_raw")
            
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        # Initialize pipeline status
        if 'pipeline_initialized' not in st.session_state:
            try:
                with st.spinner("Initializing RAG pipeline..."):
                    st.session_state.pipeline = SportsRAGPipeline()
                    st.session_state.pipeline_initialized = True
                st.success("✅ Pipeline ready!")
            except Exception as e:
                st.error(f"❌ Failed to initialize pipeline: {e}")
                st.session_state.pipeline_initialized = False
        else:
            st.success("✅ Pipeline ready!")
    
    # Main content
    st.markdown("---")
    
    # Query input
    query = st.text_area(
        "Enter your sports analytics question:",
        value=st.session_state.get('query', ''),
        height=100,
        placeholder="e.g., What are the key performance metrics for Manchester City?"
    )
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("🚀 Process Query", type="primary", use_container_width=True)
    
    # Process the query
    if process_button and query.strip():
        st.session_state.query = query
        
        try:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process the query
            status_text.text("Processing query...")
            progress_bar.progress(25)
            
            start_time = time.time()
            response = st.session_state.pipeline.answer_complex_query(query)
            processing_time = time.time() - start_time
            
            # Add processing time to response
            response['processing_time'] = processing_time
            
            progress_bar.progress(100)
            status_text.text("✅ Query processed successfully!")
            
            # Store response in session state
            st.session_state.last_response = response
            
            # Display results
            st.markdown("---")
            st.markdown(f"### 📊 Results for: *{query}*")
            
            # Display metrics
            display_metrics(response)
            
            # Display sub-questions
            display_sub_questions(response.get('sub_questions', []))
            
            # Display final answer
            display_final_answer(response.get('final_answer', 'No answer generated'))
            
            # Display sub-answers
            display_sub_answers(response.get('sub_answers', []))
            
            # Show raw response if requested
            if st.session_state.get('show_raw', False):
                with st.expander("🔧 Raw Response"):
                    st.json(response)
            
        except Exception as e:
            st.error(f"❌ Error processing query: {e}")
            logger.error(f"Error in Streamlit app: {e}")
    
    # Display previous results if available
    elif 'last_response' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Previous Results")
        
        response = st.session_state.last_response
        display_metrics(response)
        display_sub_questions(response.get('sub_questions', []))
        display_final_answer(response.get('final_answer', 'No answer generated'))
        display_sub_answers(response.get('sub_answers', []))
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🚀 Powered by LangChain, Pinecone, Groq, and Nomic Embeddings<br>
        Advanced RAG System for Sports Analytics
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 