from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from src.config import Config
from src.core.auth import get_azure_token_provider

def get_embedding_function():
    """
    Returns the Azure OpenAI Embedding model compatible with LlamaIndex.
    """
    token_provider = get_azure_token_provider()
    
    embed_model = AzureOpenAIEmbedding(
        model_name="text-embedding-3-large",  # Generic model name required by library
        deployment_name=Config.AZURE_EMBEDDING_DEPLOYMENT, # Specific deployment from .env
        api_version=Config.AZURE_API_VERSION,
        azure_endpoint=Config.AZURE_ENDPOINT,
        azure_ad_token_provider=token_provider
    )
    return embed_model
