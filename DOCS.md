# Charcha Documentation

This document provides more detailed information about using Charcha for document intelligence and exploration.

## API Reference

The RAG service API is available at http://localhost:8000 with the following endpoints:

### Upload Documents

```
POST /upload_documents
```

**Parameters:**
- `files`: List of files to upload (multipart/form-data)
- `collection_name`: Name for the collection (string)

**Example (using curl):**
```bash
curl -X POST "http://localhost:8000/upload_documents" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "collection_name=my_research"
```

**Response:**
```json
{
  "message": "Successfully processed 2 documents",
  "collection_name": "my_research",
  "document_count": 45
}
```

### Query Collection

```
POST /query
```

**Parameters (JSON):**
```json
{
  "query": "What are the main findings?",
  "collection_name": "my_research",
  "model_name": "phi4"
}
```

**Example (using curl):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main findings?", "collection_name": "my_research", "model_name": "phi4"}'
```

**Response:**
```json
{
  "response": "The main findings from the documents are...",
  "source_documents": [
    {
      "content": "The study demonstrated that...",
      "metadata": {"source": "document1.pdf", "page": 5}
    },
    ...
  ]
}
```

### List Collections

```
GET /collections
```

**Example (using curl):**
```bash
curl -X GET "http://localhost:8000/collections"
```

**Response:**
```json
{
  "collections": ["my_research", "project_x", "technical_docs"]
}
```

### Delete Collection

```
DELETE /collections/{collection_name}
```

**Example (using curl):**
```bash
curl -X DELETE "http://localhost:8000/collections/my_research"
```

**Response:**
```json
{
  "message": "Collection 'my_research' deleted successfully"
}
```

### Get Available Models

```
GET /models
```

**Example (using curl):**
```bash
curl -X GET "http://localhost:8000/models"
```

**Response:**
```json
{
  "models": ["phi4:latest", "gemma3:12b", "mxbai-embed-large:latest", "llama3:8b"]
}
```

## Use Cases

Here are some example use cases for Charcha:

### Research Paper Analysis

1. Upload a collection of research papers in PDF format
2. Query: "What are the common methodologies used across these papers?"
3. Query: "Summarize the key findings from papers published after 2020"
4. Query: "What gaps in research are identified across these papers?"

### Technical Documentation

1. Upload technical documentation for a software project
2. Query: "How do I configure the authentication module?"
3. Query: "What are the API endpoints available for user management?"
4. Query: "Show me examples of error handling in the code"

### Legal Document Review

1. Upload a collection of contracts and legal agreements
2. Query: "What are the termination clauses in these agreements?"
3. Query: "Identify any inconsistencies in payment terms across contracts"
4. Query: "Summarize the intellectual property rights mentioned in these documents"

### Learning and Education

1. Upload textbooks or course materials
2. Query: "Explain the concept of neural networks in simple terms"
3. Query: "Create a study guide for the key topics in this material"
4. Query: "What are the differences between supervised and unsupervised learning?"

## Performance Optimization

To optimize the performance of your RAG system:

### Chunk Size Optimization

Different document types benefit from different chunk sizes:
- Academic papers: 750-1000 tokens with 150-200 token overlap
- Technical documentation: 500-750 tokens with 100-150 token overlap
- Narrative content: 1000-1500 tokens with 200-300 token overlap

### Model Selection

- For quick responses: Use smaller models like phi3:mini
- For complex reasoning: Use larger models like gemma3:12b
- For specialized domains: Consider using domain-specific models if available

### Embedding Quality

The quality of embeddings significantly affects retrieval performance:
- mxbai-embed-large provides an excellent balance of quality and speed
- For specialized domains, consider using domain-specific embedding models

## Troubleshooting

### Common Issues

1. **Slow Document Processing**
   - Reduce the file size or split large documents
   - Adjust chunk size to be larger (reduces total number of embeddings)

2. **Poor Query Results**
   - Try reformulating the query to be more specific
   - Increase the number of chunks retrieved (k parameter)
   - Check if the document contains the information you're looking for

3. **Out of Memory Errors**
   - Reduce the number of documents processed simultaneously
   - Use smaller embedding or LLM models
   - Increase Docker memory allocation

4. **Container Startup Issues**
   - Check if Ollama is running properly
   - Ensure the required models are downloaded
   - View logs with `docker-compose logs -f`
