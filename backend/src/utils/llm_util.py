from langchain_openai import AzureChatOpenAI
from config.settings import settings
from azure.identity import DefaultAzureCredential,get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# Initialize the LLM
llm = AzureChatOpenAI(
    #openai_api_key=settings.azure_openai_api_key,
    azure_ad_token_provider=token_provider,
    openai_api_version=settings.api_version,
    azure_endpoint=settings.azure_openai_endpoint,
    deployment_name=settings.deployment_name
)