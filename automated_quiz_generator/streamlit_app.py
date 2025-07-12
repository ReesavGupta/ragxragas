import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Automated Quiz Generator")

# Upload PDF
st.header("1. Upload Educational PDF Document")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    with st.spinner("Uploading and processing..."):
        response = requests.post(f"{API_URL}/upload/", files=files)
    if response.ok:
        st.success(response.json().get("message", "Upload successful!"))
    else:
        st.error("Upload failed.")

# Generate Quiz
st.header("2. Generate Quiz")
user_id = st.text_input("User ID", value="user123")
query = st.text_input("Quiz Topic/Query", value="")
difficulty = st.selectbox("Difficulty (leave blank for auto)", ["", "easy", "medium", "hard"])
if st.button("Generate Quiz"):
    params = {"query": query, "user_id": user_id}
    if difficulty:
        params["difficulty"] = difficulty
    with st.spinner("Generating quiz..."):
        response = requests.get(f"{API_URL}/generate_quiz/", params=params)
    if response.ok:
        quiz = response.json().get("quiz", "No quiz generated.")
        st.text_area("Generated Quiz", quiz, height=300)
        st.session_state["last_quiz"] = quiz
        st.session_state["last_user_id"] = user_id
    else:
        st.error("Quiz generation failed.")

# Submit Score
st.header("3. Submit Your Score")
score = st.number_input("Your Score (out of 5)", min_value=0, max_value=5, value=0)
if st.button("Submit Score"):
    user_id_submit = st.session_state.get("last_user_id", user_id)
    params = {"user_id": user_id_submit, "score": score}
    with st.spinner("Submitting score..."):
        response = requests.post(f"{API_URL}/submit_score/", params=params)
    if response.ok:
        st.success(response.json().get("message", "Score submitted!"))
    else:
        st.error("Failed to submit score.") 