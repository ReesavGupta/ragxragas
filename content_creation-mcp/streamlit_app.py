import streamlit as st
import requests
import datetime
import re
import yaml
import os
import mcp_client

API_URL = "http://localhost:8000"

IDEAS_DIR = "content-workspace/ideas"
GENERATED_DIR = "content-workspace/generated"

st.set_page_config(page_title="Content Creation Assistant", layout="wide")
st.title("Content Creation Assistant")

st.header("💡 Idea Capture Chat")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Helper to extract metadata from user input (simple heuristic)
def extract_metadata(user_input):
    # Title: first sentence or up to 10 words
    title = user_input.strip().split('.')[0]
    title = ' '.join(title.split()[:10])
    # Summary: everything after title
    summary = user_input.strip()
    # Tags: extract words after 'about', 'on', or fallback to keywords
    tags = []
    match = re.search(r'about ([\w\s,]+)', user_input, re.IGNORECASE)
    if match:
        tags = [t.strip() for t in match.group(1).split(',')]
    else:
        tags = [w for w in title.lower().split() if len(w) > 3]
    return title, summary, tags

# Helper to list idea files
def list_idea_files():
    try:
        files = mcp_client.list_directory("ideas")
        return [f for f in files if f.endswith(".md")]
    except Exception:
        pass
    return []

# Helper to read idea file and parse metadata
def read_idea_file(filename):
    try:
        content = mcp_client.read_file(f"ideas/{filename}")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                meta = yaml.safe_load(parts[1])
                return meta, content
    except Exception:
        pass
    return None, None

# Chat input
user_input = st.text_input("Type your blog idea:", "")
if st.button("Submit Idea") and user_input:
    title, summary, tags = extract_metadata(user_input)
    today = datetime.date.today().isoformat()
    safe_title = re.sub(r'[^a-zA-Z0-9\- ]', '', title.replace(' ', '-')).lower()
    filename = f"{today}-{safe_title}.md"
    frontmatter = {
        'title': title,
        'date': today,
        'tags': tags,
        'summary': summary,
        'published_url': '',
        'published_date': ''
    }
    markdown = f"---\n{yaml.dump(frontmatter)}---\n\n# {title}\n\n{summary}\n"
    try:
        mcp_client.write_file(f'ideas/{filename}', markdown)
        st.session_state['chat_history'].append(("user", user_input))
        st.session_state['chat_history'].append(("assistant", f"Idea saved as `{filename}`!"))
    except Exception as e:
        st.session_state['chat_history'].append(("user", user_input))
        st.session_state['chat_history'].append(("assistant", f"Error saving idea: {e}"))

st.header("📝 Generate Draft from Idea")
idea_files = list_idea_files()
if idea_files:
    selected_idea = st.selectbox("Select an idea to generate a draft:", idea_files)
    if st.button("Generate Draft"):
        meta, _ = read_idea_file(selected_idea)
        if meta:
            with st.spinner("Generating draft with OpenAI..."):
                import requests
                resp = requests.post(f"http://localhost:8000/generate_article", json={
                    "title": meta.get("title", ""),
                    "summary": meta.get("summary", ""),
                    "tags": meta.get("tags", [])
                })
                if resp.status_code == 200:
                    draft = resp.json()["draft"]
                    today = meta.get("date") or datetime.date.today().isoformat()
                    safe_title = re.sub(r'[^a-zA-Z0-9\- ]', '', meta.get("title", "").replace(' ', '-')).lower()
                    draft_filename = f"{today}-{safe_title}-draft.md"
                    draft_content = f"---\n{yaml.dump(meta)}---\n\n{draft}\n"
                    try:
                        mcp_client.write_file(f"generated/{draft_filename}", draft_content)
                        st.success(f"Draft saved as generated/{draft_filename}")
                        st.markdown("### Draft Preview:")
                        st.markdown(draft)
                    except Exception as e:
                        st.error(f"Error saving draft: {e}")
                else:
                    st.error(f"Error generating draft: {resp.text}")
else:
    st.info("No ideas found. Please add an idea first.")

st.header("📂 Content File Browser & Preview")

folders = [
    ("Ideas", "ideas", "💡 Idea"),
    ("Generated Drafts", "generated", "📝 Draft"),
    ("Published", "published", "✅ Published")
]

for label, folder, status in folders:
    st.subheader(f"{status} — {label}")
    files = []
    try:
        files = mcp_client.list_directory(folder)
        files = [f for f in files if f.endswith(".md")]
    except Exception:
        pass
    if files:
        selected = st.selectbox(f"Select a file from {label}", files, key=folder)
        if st.button(f"Preview {label} File", key=f"preview_{folder}"):
            try:
                content = mcp_client.read_file(f"{folder}/{selected}")
                st.markdown(f"#### {selected}")
                st.markdown(content)
            except Exception as e:
                st.error(f"Error reading file: {e}")
    else:
        st.info(f"No files found in {label}.")

# Display chat history
for sender, msg in st.session_state['chat_history']:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Assistant:** {msg}") 