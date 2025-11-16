"""
Ollama API client
"""
import json
import urllib.parse
import urllib.request
from typing import List, Generator, Optional


class OllamaClient:
    """Ollama API client"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:11434"):
        """
        Initialize Ollama client
        
        Args:
            api_url: Ollama API base URL
        """
        self.api_url = api_url

    def fetch_models(self) -> List[str]:
        """
        Fetch available models
        
        Returns:
            List of model names
        """
        try:
            with urllib.request.urlopen(
                urllib.parse.urljoin(self.api_url, "/api/tags")
            ) as response:
                data = json.load(response)
                models = [model["name"] for model in data["models"]]
                return models
        except Exception:
            return []

    def chat_stream(self, model: str, messages: List[dict]) -> Generator[str, None, None]:
        """
        Stream chat response
        
        Args:
            model: Model name
            messages: Chat messages in API format
            
        Yields:
            Response content chunks
        """
        request = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/chat"),
            data=json.dumps({
                "model": model,
                "messages": messages,
                "stream": True,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as resp:
                for line in resp:
                    data = json.loads(line.decode("utf-8"))
                    if "message" in data:
                        yield data["message"]["content"]
        except Exception as e:
            raise Exception(f"API request failed: {e}")

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a model
        
        Args:
            model_name: Name of model to delete
            
        Returns:
            True if successful
        """
        req = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/delete"),
            data=json.dumps({"name": model_name}).encode("utf-8"),
            method="DELETE",
        )
        try:
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except Exception:
            return False

    def download_model(self, model_name: str, insecure: bool = False) -> Generator[str, None, None]:
        """
        Download a model
        
        Args:
            model_name: Name of model to download
            insecure: Allow insecure connections
            
        Yields:
            Status messages
        """
        req = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/pull"),
            data=json.dumps({
                "name": model_name,
                "insecure": insecure,
                "stream": True
            }).encode("utf-8"),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                for line in response:
                    data = json.loads(line.decode("utf-8"))
                    log = data.get("error") or data.get("status") or "No response"
                    if "status" in data:
                        total = data.get("total")
                        completed = data.get("completed", 0)
                        if total:
                            log += f" [{completed}/{total}]"
                    yield log
        except Exception as e:
            yield f"Failed to download model: {e}"

