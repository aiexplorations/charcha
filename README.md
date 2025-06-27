# Charcha - Document Intelligence with RAG

Charcha (meaning "conversation" in Hindi) is a powerful and flexible Retrieval-Augmented Generation (RAG) based chatbot system. It allows you to point an AI chatbot to specific documents on your disk and have natural conversations to explore the knowledge contained within them.

![Charcha RAG System](https://raw.githubusercontent.com/aiexplorations/charcha/main/images/charcha-overview.png)

## ✨ Features

- **Document Intelligence**: Upload and process various document types (PDF, TXT, DOCX, CSV, HTML, MD)
- **Knowledge Organization**: Create separate collections for different topics or projects
- **Semantic Search**: Generate embeddings from documents using Ollama's mxbai-embed-large model
- **Natural Language Interface**: Query your documents in everyday language
- **User-friendly Interface**: Powered by OpenWebUI for smooth interaction
- **Privacy-focused**: Uses your locally running Ollama instance (no data sent to external APIs)
- **Flexible Model Support**: Configured for Phi4, Gemma3:12b, and other models available in Ollama

## 🚀 Quick Start

### Prerequisites

- macOS or Linux with Docker and Docker Compose installed
- [Ollama](https://ollama.ai/) running locally at localhost:11434
- Required models pulled in Ollama:
  - phi4:latest (for generation)
  - gemma3:12b (for generation)
  - mxbai-embed-large:latest (for embeddings)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/aiexplorations/charcha.git
   cd charcha
   ```

2. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

3. Pull the required models (if not already done):
   ```bash
   ollama pull phi4:latest
   ollama pull gemma3:12b
   ollama pull mxbai-embed-large:latest
   ```

4. Start the services:
   ```bash
   # For macOS users:
   ./build-for-mac.sh
   
   # For Linux users:
   ./start.sh
   ```

5. Access the OpenWebUI interface at http://localhost:3000

## 📚 Usage Guide

### Setting Up Document Collections

1. Go to the RAG API interface at http://localhost:8000/docs
2. Use the `/upload_documents` endpoint to create a new collection
   - Select multiple files to upload
   - Provide a name for your collection
3. Wait for the system to process your documents and create embeddings

### Querying Your Documents

There are two ways to query your document collections:

**Option 1: Using the API directly**
1. Go to http://localhost:8000/docs
2. Use the `/query` endpoint
3. Provide your query and the name of the collection to search
4. Optionally specify a different model (default is phi4)

**Option 2: Using OpenWebUI**
1. Go to http://localhost:3000
2. Create a new chat
3. Ask questions about your documents
4. The system will retrieve relevant context and generate answers

### Managing Collections

- List all collections: GET `/collections`
- Delete a collection: DELETE `/collections/{collection_name}`
- View available models: GET `/models`

## 🔧 Architecture

Charcha consists of three main components:

1. **OpenWebUI**: Frontend interface for chatting with your documents
2. **Ollama**: Local LLM service providing:
   - Text generation (phi4, gemma3:12b)
   - Text embeddings (mxbai-embed-large)
3. **RAG Service**: Custom FastAPI backend that handles:
   - Document processing and embedding generation
   - Vector database management (using FAISS)
   - Query processing and retrieval

### Technical Flow

1. **Document Processing Stage**:
   - Documents are loaded and chunked to manageable sizes
   - Each chunk is embedded using mxbai-embed-large via Ollama
   - Embeddings are stored in FAISS for efficient vector search

2. **Query Stage**:
   - User query is embedded using the same embedding model
   - Vector similarity search retrieves relevant document chunks
   - Retrieved context is sent along with the query to the LLM
   - LLM generates a response based on the query and context

## 🛠️ Advanced Configuration

### Models

The system is pre-configured to use:
- `phi4:latest` (default LLM for generation)
- `gemma3:12b` (alternative LLM for generation)
- `mxbai-embed-large:latest` (for document embeddings)

You can use any other model available in Ollama by:
1. Pulling the model: `ollama pull <model-name>`
2. Specifying it when querying: `model_name` parameter in API

### Text Chunking Parameters

Edit `app/main.py` to change:
- `CHUNK_SIZE`: Size of text chunks (default: 1000 tokens)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 tokens)

### Adding Support for More Document Types

Extend the `LOADER_MAPPING` in `app/utils.py` to support additional document formats.

## 🔍 Troubleshooting

- **OpenWebUI not connecting to Ollama**: Check if Ollama is running with `curl localhost:11434/api/tags`
- **RAG service failing to start**: Check Docker logs with `docker-compose logs -f rag-service`
- **Missing models**: Verify Ollama has the required models with `ollama list`
- **Slow response times**: Try reducing the number of chunks retrieved during search (adjust the `k` parameter)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai/) for providing local LLM capabilities
- [OpenWebUI](https://github.com/open-webui/open-webui) for the frontend interface
- [LangChain](https://github.com/langchain-ai/langchain) for RAG components
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector search
