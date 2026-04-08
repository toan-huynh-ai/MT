from azure.identity import ClientSecretCredential, get_bearer_token_provider
from src.config import Config

def get_azure_token_provider():
    """Returns a token provider for Azure OpenAI authentication."""
    # Ensure config is valid before proceeding
    Config.validate()
    
    credential = ClientSecretCredential(
        tenant_id=Config.TENANT_ID, 
        client_id=Config.CLIENT_ID, 
        client_secret=Config.CLIENT_SECRET
    )
    
    # Standard scope for Azure Cognitive Services
    token_provider = get_bearer_token_provider(
        credential, 
        "https://cognitiveservices.azure.com/.default"
    )
    return token_provider
