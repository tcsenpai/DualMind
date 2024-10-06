import requests

class OllamaClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def generate(self, model, prompt, system_prompt):
        url = f"{self.endpoint}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()["response"]

    def get_available_models(self):
        url = f"{self.endpoint}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        return [model['name'] for model in response.json()['models']]