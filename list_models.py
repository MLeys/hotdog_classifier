import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

url = "https://openrouter.AI/api/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "http://localhost:5000"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("\nAvailable Models:")
    models = response.json()
    for model in models:
        print(f"\nModel: {model.get('id')}")
        print(f"Context Length: {model.get('context_length')}")
        print(f"Vision: {model.get('vision', False)}")
except Exception as e:
    print(f"Error: {e}")