#!/bin/bash

# Charcha CLI - A simple utility script for managing Charcha

function show_help {
    echo "Charcha CLI - Manage your document intelligence system"
    echo ""
    echo "Usage: ./charcha-cli.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start             Start all Charcha services"
    echo "  stop              Stop all Charcha services"
    echo "  status            Check the status of Charcha services"
    echo "  logs              View logs from all services"
    echo "  logs rag          View logs from only the RAG service"
    echo "  logs web          View logs from only the OpenWebUI service"
    echo "  upload [folder]   Help with uploading a folder of documents"
    echo "  models            List available models in Ollama"
    echo "  rebuild           Rebuild all containers"
    echo "  help              Show this help message"
    echo ""
}

function check_ollama {
    echo "Checking if Ollama is running..."
    if ! curl -s localhost:11434/api/tags > /dev/null; then
        echo "❌ Error: Ollama is not running at localhost:11434"
        echo "Please start Ollama first with: ollama serve"
        return 1
    else
        echo "✅ Ollama is running"
        return 0
    fi
}

function start_services {
    if check_ollama; then
        echo "Starting Charcha services..."
        if [[ "$(uname)" == "Darwin" ]]; then
            ./build-for-mac.sh
        else
            ./start.sh
        fi
    fi
}

function stop_services {
    echo "Stopping Charcha services..."
    docker-compose down
    echo "✅ Services stopped"
}

function check_status {
    echo "Checking Charcha services status..."
    docker-compose ps
    
    # Check if API is accessible
    if curl -s localhost:8000 > /dev/null; then
        echo "✅ RAG API is accessible"
    else
        echo "❌ RAG API is not accessible"
    fi
    
    # Check if OpenWebUI is accessible
    if curl -s localhost:3000 > /dev/null; then
        echo "✅ OpenWebUI is accessible"
    else
        echo "❌ OpenWebUI is not accessible"
    fi
}

function show_logs {
    if [ "$1" == "rag" ]; then
        docker-compose logs -f rag-service
    elif [ "$1" == "web" ]; then
        docker-compose logs -f openwebui
    else
        docker-compose logs -f
    fi
}

function list_models {
    echo "Fetching available models from Ollama..."
    curl -s localhost:11434/api/tags | jq '.models[] | .name'
}

function help_upload {
    local folder=$1
    
    if [ -z "$folder" ]; then
        echo "Please specify a folder containing documents to upload"
        echo "Usage: ./charcha-cli.sh upload /path/to/documents"
        return 1
    fi
    
    if [ ! -d "$folder" ]; then
        echo "❌ Error: $folder is not a valid directory"
        return 1
    fi
    
    echo "📂 Documents folder: $folder"
    
    # Count files by type
    echo "Found the following documents:"
    find "$folder" -type f -name "*.pdf" | wc -l | xargs echo "  PDF files:"
    find "$folder" -type f -name "*.txt" | wc -l | xargs echo "  Text files:"
    find "$folder" -type f -name "*.docx" | wc -l | xargs echo "  Word files:"
    find "$folder" -type f -name "*.csv" | wc -l | xargs echo "  CSV files:"
    
    echo ""
    echo "To upload these documents, use the API endpoint:"
    echo "http://localhost:8000/docs#/default/upload_documents_upload_documents_post"
    echo ""
    echo "Or use the following curl command (replace collection_name):"
    echo ""
    echo "curl -X 'POST' \\"
    echo "  'http://localhost:8000/upload_documents' \\"
    echo "  -H 'accept: application/json' \\"
    echo "  -H 'Content-Type: multipart/form-data' \\"
    
    # Generate example curl command with up to 5 files
    count=0
    for file in $(find "$folder" -type f | head -n 5); do
        echo "  -F 'files=@$file' \\"
        count=$((count+1))
    done
    
    if [ $count -eq 5 ]; then
        echo "  # ... add more files as needed \\"
    fi
    
    echo "  -F 'collection_name=my_collection'"
}

function rebuild_services {
    if check_ollama; then
        echo "Rebuilding Charcha services..."
        if [[ "$(uname)" == "Darwin" ]]; then
            ./rebuild.sh
        else
            docker-compose down
            docker-compose up -d --build
        fi
    fi
}

# Main command router
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs "$2"
        ;;
    models)
        list_models
        ;;
    upload)
        help_upload "$2"
        ;;
    rebuild)
        rebuild_services
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run './charcha-cli.sh help' to see available commands"
        exit 1
        ;;
esac
