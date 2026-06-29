import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    #azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("API_VERSION")
    deployment_name=os.getenv("DEPLOYMENT_NAME")
    # Azure Blob Storage settings
    storage_account_url = os.getenv("STORAGE_ACCOUNT_URL")
    container_name = os.getenv("CONTAINER_NAME")
    blob_name = os.getenv("BLOB_NAME")


settings = Settings()