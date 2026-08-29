"""
LangChain Version - Configuration
Loads .env file and sets environment variables for LangChain
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

# Set LangChain-compatible env variables BEFORE LangChain imports
_api_key = os.getenv("AZURE_AI_API_KEY", "")
_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hquan8696-5179-resource.services.ai.azure.com")
_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

os.environ["AZURE_OPENAI_API_KEY"] = _api_key
os.environ["AZURE_OPENAI_ENDPOINT"] = _endpoint
os.environ["OPENAI_API_VERSION"] = _api_version
os.environ["AZURE_OPENAI_API_VERSION"] = _api_version

# Azure OpenAI config
AZURE_API_KEY = _api_key
AZURE_ENDPOINT = _endpoint
AZURE_API_VERSION = _api_version
CHAT_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_AI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large")

print(f"Config loaded: endpoint={AZURE_ENDPOINT}, deployment={CHAT_DEPLOYMENT}, key={AZURE_API_KEY[:10] if AZURE_API_KEY else 'None'}...")
