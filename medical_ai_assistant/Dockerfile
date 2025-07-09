# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .
COPY .env .env

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# Default command: run both API and dashboard using bash (for dev/demo)
CMD ["bash", "-c", "uvicorn medical_ai_assistant.src.api:app --host 0.0.0.0 --port 8000 & streamlit run medical_ai_assistant/src/dashboard.py --server.port 8501 --server.address 0.0.0.0"] 