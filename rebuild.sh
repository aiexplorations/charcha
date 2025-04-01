#!/bin/bash

# Exit on any error
set -e

echo "Rebuilding Charcha services..."

# Check if Ollama is running locally
echo "Checking if Ollama is running at localhost:11434..."
if ! curl -s localhost:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama is not running at localhost:11434"
    echo "Please start Ollama first with: ollama serve"
    exit 1
fi
echo "✅ Ollama is running"

# Stop and remove existing containers
echo "Stopping and removing existing containers..."
docker-compose down || true

# Remove existing images to force rebuilding
echo "Removing existing images..."
docker rmi $(docker images -q charcha_rag-service) 2>/dev/null || true

# Build the images with no-cache to ensure a clean build
echo "Building services..."
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi

# Start the services
echo "Starting services..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start services. Check the error messages above."
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
echo "Models configured:"
echo "- phi4:latest (default LLM)"
echo "- gemma3:12b (alternative LLM)"
echo "- mxbai-embed-large:latest (embeddings)"