FROM python:3.10-slim

WORKDIR /workspace

COPY requirements-simple.txt .
COPY app /workspace/app

# Update pip and install packages in steps for better error visibility
RUN pip install --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn pydantic python-multipart && \
    pip install --no-cache-dir requests python-dotenv && \
    pip install --no-cache-dir pypdf && \
    pip install --no-cache-dir langchain langchain-community && \
    pip install --no-cache-dir faiss-cpu

# Install system dependencies for networking and troubleshooting
# Using netcat-openbsd instead of just netcat
RUN apt-get update && apt-get install -y curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /data /embeddings

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]