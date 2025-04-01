import os
import requests
import json
from typing import Dict, List, Any, Optional

class CharChaAPI:
    """
    Client class for interacting with the CharCha RAG API
    """
    
    def __init__(self, base_url: str = "http://rag-service:8000"):
        self.base_url = base_url
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        response = requests.get(f"{self.base_url}/collections")
        response.raise_for_status()
        return response.json().get("collections", [])
    
    def query_collection(self, collection_name: str, query: str) -> Dict[str, Any]:
        """Query a specific collection"""
        response = requests.post(
            f"{self.base_url}/query",
            json={"collection_name": collection_name, "query": query}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection"""
        response = requests.delete(f"{self.base_url}/collections/{collection_name}")
        response.raise_for_status()
        return response.json()

class OpenWebUIIntegration:
    """
    Integration with OpenWebUI for RAG functionality
    """
    
    def __init__(
        self, 
        openwebui_url: str = "http://openwebui:8080",
        api_client: Optional[CharChaAPI] = None
    ):
        self.openwebui_url = openwebui_url
        self.api_client = api_client or CharChaAPI()
    
    def register_rag_endpoints(self):
        """
        Register the RAG API endpoints with OpenWebUI
        This is a placeholder as OpenWebUI integration will depend on its API
        """
        # This would be implemented based on OpenWebUI's plugin or extension system
        # For now, we'll provide the integration instructions in the README
        pass
    
    def get_plugin_manifest(self) -> Dict[str, Any]:
        """
        Generate a plugin manifest for OpenWebUI
        """
        return {
            "schema_version": "v1",
            "name_for_human": "Charcha Document Intelligence",
            "name_for_model": "charcha",
            "description_for_human": "Query your documents using RAG technology.",
            "description_for_model": "This plugin allows querying document collections using RAG.",
            "auth": {
                "type": "none"
            },
            "api": {
                "type": "openapi",
                "url": f"{self.api_client.base_url}/openapi.json"
            },
            "logo_url": f"{self.api_client.base_url}/logo.png",
            "contact_email": "support@example.com",
            "legal_info_url": "https://example.com/legal"
        }

if __name__ == "__main__":
    # Example usage
    client = CharChaAPI()
    
    # List collections
    collections = client.list_collections()
    print(f"Available collections: {collections}")
    
    # Example query if collections exist
    if collections:
        collection_name = collections[0]
        response = client.query_collection(
            collection_name=collection_name,
            query="What are the main topics covered in these documents?"
        )
        print(f"Query response: {response['response']}")
