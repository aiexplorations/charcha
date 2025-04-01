import os
import requests
import time
import sys

OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://host.docker.internal:11434")
MODELS_TO_PULL = [
    "phi4:latest", 
    "gemma3:12b",
    "mxbai-embed-large:latest"  # Added embedding model
]

def wait_for_ollama():
    """Wait for Ollama service to be available"""
    max_retries = 30
    retry_interval = 2  # seconds
    
    print("Checking connection to local Ollama service...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags")
            if response.status_code == 200:
                print("Successfully connected to local Ollama service!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Waiting for Ollama connection... {i+1}/{max_retries}")
        time.sleep(retry_interval)
    
    print("Could not connect to local Ollama service. Please ensure Ollama is running at localhost:11434")
    return False

def check_models():
    """Check if required models are available, pull if not"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags")
        response.raise_for_status()
        
        available_models = [model['name'] for model in response.json().get("models", [])]
        missing_models = [model for model in MODELS_TO_PULL if model not in available_models]
        
        if not missing_models:
            print("All required models are already available!")
            return True
        
        print(f"Need to pull these models: {missing_models}")
        for model in missing_models:
            print(f"Pulling model: {model}")
            pull_response = requests.post(
                f"{OLLAMA_API_BASE_URL}/api/pull",
                json={"name": model}
            )
            
            if pull_response.status_code == 200:
                print(f"Successfully pulled model: {model}")
            else:
                print(f"Failed to pull model: {model}")
                print(f"Response: {pull_response.text}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error checking models: {str(e)}")
        return False

def list_models():
    """List available models in Ollama"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("\nAvailable models:")
            for model in models:
                print(f" - {model['name']}")
        else:
            print("Failed to list models")
    except requests.exceptions.RequestException as e:
        print(f"Error listing models: {str(e)}")

if __name__ == "__main__":
    if wait_for_ollama():
        check_models()
        list_models()
    else:
        sys.exit(1)
