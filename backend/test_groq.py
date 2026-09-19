# c:/Users/Anvesha Garg/Desktop/Foreman/backend/test_groq.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from backend/.env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    # If .env is not loaded, manually paste your key here temporarily to test:
    api_key = "gsk_YourActualGroqApiKeyHere"

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

try:
    models = client.models.list()
    print("\nSUCCESS! Active Models on your Key:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print("\nAPI Error:", e)