# Product Requirements Document (PRD)

## Product Name
Content Creation Assistant

## Objective
Build a full-stack, GUI-based tool that enables content teams to manage the complete blog workflow — from idea capture to AI-powered draft generation to publishing on Medium — using a chat-first interface and local file operations via MCP.

## Target Users
Marketing and content teams, especially solo users or small teams managing Medium blogs.

## Key Features
1. **Chat-Based Idea Capture**
    - Chat interface for capturing blog ideas.
    - Extracts metadata (title, summary, tags).
    - Saves ideas as markdown files with YAML frontmatter in `ideas/`.
    - Filenames: `YYYY-MM-DD-idea-title.md`.

2. **AI-Powered Content Generation**
    - Command to generate article drafts from ideas.
    - Loads idea, calls OpenAI API, saves draft in `generated/`.
    - Preview draft in chat interface.

3. **Content Review & Editing Dashboard**
    - File browser for `ideas/`, `generated/`, `published/`.
    - Status tracking (idea, drafted, published).
    - In-app content viewing and editing.
    - Move files from `generated/` to `published/`.

4. **One-Click Medium Publishing**
    - Button to publish approved articles to Medium.
    - Posts to Medium via API, updates local file with URL and date.
    - Success notification in chat and dashboard.

## Architecture Overview
- **Frontend:** Streamlit (chat interface, file dashboard)
- **Backend:** FastAPI (REST endpoints for OpenAI, MCP, Medium)
- **File Ops:** MCP Client (Python wrappers)
- **Auth:** .env file for API tokens
- **Storage:** Local files (`content-workspace/`)

## Directory Structure
```
content-workspace/
├── ideas/
├── generated/
├── published/
├── templates/
```

## Authentication
- API keys in `.env`:
    - `OPENAI_API_KEY`
    - `MEDIUM_INTEGRATION_TOKEN`

## Functional Components
| Component           | Description                                      |
|---------------------|--------------------------------------------------|
| streamlit_app.py    | Chat UI, file browser, dashboard                 |
| fastapi_server.py   | REST API for OpenAI, MCP, Medium                 |
| mcp_client.py       | File operations (read, write, move, list)        |
| openai_client.py    | Calls OpenAI GPT for content generation          |
| medium_client.py    | Publishes articles to Medium                     |
| template_loader.py  | Loads markdown templates                         |

## User Stories
- As a content creator, I want to capture blog ideas in a chat so I can easily start new articles.
- As a user, I want to generate article drafts from my ideas using AI so I can save time.
- As an editor, I want to review and edit drafts in-app so I can refine content before publishing.
- As a publisher, I want to publish approved articles to Medium with one click.

## Success Metrics
- End-to-end flow completion rate (idea → draft → published)
- Time saved per article (compared to manual process)
- Internal feedback from marketing/content stakeholders

## Milestones
| Week | Deliverable                                 |
|------|---------------------------------------------|
| 1    | FastAPI backend + MCP file ops ready        |
| 2    | Chat idea capture + markdown generation     |
| 3    | Draft generation via OpenAI                 |
| 4    | Streamlit file browser + preview interface  |
| 5    | Medium publishing + status updates          |
| 6    | Full testing, polish, README, deploy locally|

## Example Markdown Format
```
---
title: MCP for Developers
date: 2025-07-10
tags: [MCP, developer tools, AI]
summary: How developers can integrate Model Context Protocol into their systems
published_url:
published_date:
---

## Introduction
...
## What is MCP?
...
## How to Use MCP in Developer Workflows
...
## Conclusion
...
``` 