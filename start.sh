#!/bin/bash

# Exit on any error
set -e

echo "Starting Charcha - Document Intelligence Chatbot"

# Check if Ollama is running locally
echo "Checking if Ollama is running at localhost:11434..."
if ! curl -s localhost:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama is not running at localhost:11434"
    echo "Please start Ollama first with: ollama serve"
    exit 1
fi
echo "✅ Ollama is running at localhost:11434"

# Check for required models
echo "Checking for required models..."
REQUIRED_MODELS=("phi4:latest" "gemma3:12b" "mxbai-embed-large:latest")
MODELS_JSON=$(curl -s localhost:11434/api/tags)
MISSING_MODELS=0

for MODEL in "${REQUIRED_MODELS[@]}"; do
    if [[ $MODELS_JSON != *"$MODEL"* ]]; then
        echo "❓ Model not found: $MODEL"
        echo "   Attempting to pull..."
        curl -s -X POST localhost:11434/api/pull -d "{\"name\":\"$MODEL\"}"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to pull $MODEL"
            MISSING_MODELS=1
        else
            echo "✅ Successfully pulled $MODEL"
        fi
    else
        echo "✅ Found model: $MODEL"
    fi
done

if [ $MISSING_MODELS -eq 1 ]; then
    echo "⚠️ Some models could not be pulled automatically."
    echo "   Please pull them manually with ollama pull <model-name>"
    echo "   Then run this script again."
    exit 1
fi

# Build and start the containers
echo "Building and starting containers..."
if ! docker-compose up -d --build; then
    echo "❌ Error: Failed to build and start containers."
    echo "Please check the error messages above."
    exit 1
fi

# Wait for services to initialize
echo "Waiting for services to initialize..."
sleep 10

# Check if the services are actually running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Services are not running properly after initialization."
    echo "Please check docker logs with: docker-compose logs"
    exit 1
fi

echo "✅ Charcha is now running!"
echo "Access OpenWebUI at: http://localhost:3000"
echo "RAG API available at: http://localhost:8000"
echo ""
echo "Usage instructions:"
echo "1. Go to OpenWebUI and create a new chat"
echo "2. Use the RAG endpoint to upload documents: http://localhost:8000/docs"
echo "3. Query your documents through OpenWebUI or the API"
echo ""
echo "Models configured:"
echo "- phi4:latest (default LLM)"
echo "- gemma3:12b (alternative LLM)"
echo "- mxbai-embed-large:latest (embeddings)"