#!/bin/bash

# Exit on any error
set -e

echo "Building Charcha for macOS..."

# Check architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Choose the appropriate Dockerfile
if [[ "$ARCH" == "arm64" ]]; then
    echo "Using ARM64 specific Dockerfile for Apple Silicon Mac"
    cp Dockerfile.arm64 Dockerfile.mac
else
    echo "Using standard x86_64 Dockerfile"
    cp Dockerfile Dockerfile.mac
fi

# Create a temporary docker-compose file with the specific Dockerfile
cat > docker-compose.mac.yml << EOL
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    volumes:
      - ./openwebui:/app/backend/data
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_API_BASE_URL=http://host.docker.internal:11434
      - OPENAI_API_KEY=sk-xxx
      - AUTH_SECRET=my-secret-key
    extra_hosts:
      - "host.docker.internal:host-gateway"

  rag-service:
    build:
      context: .
      dockerfile: Dockerfile.mac
    container_name: rag-service
    volumes:
      - ./data:/data
      - ./embeddings:/embeddings
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_API_BASE_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOL

# Check if Ollama is running
echo "Checking if Ollama is running at localhost:11434..."
if ! curl -s localhost:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama is not running at localhost:11434"
    echo "Please start Ollama first with: ollama serve"
    exit 1
fi
echo "✅ Ollama is running"

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose -f docker-compose.mac.yml down || true

# Build and start with new docker-compose file
echo "Building and starting services..."
if ! docker-compose -f docker-compose.mac.yml up -d --build; then
    echo "❌ Error: Build failed. See above for details."
    exit 1
fi

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 5

# Check if services are running
echo "Checking service status..."
if docker-compose -f docker-compose.mac.yml ps | grep -q "Exit"; then
    echo "❌ Error: Some services failed to start. Checking logs..."
    docker-compose -f docker-compose.mac.yml logs rag-service
    exit 1
fi

echo "✅ Charcha is now running!"
echo "Access OpenWebUI at: http://localhost:3000"
echo "RAG API available at: http://localhost:8000"
echo ""
echo "To view logs:"
echo "docker-compose -f docker-compose.mac.yml logs -f"