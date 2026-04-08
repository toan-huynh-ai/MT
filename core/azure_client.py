import json
from langchain_openai import AzureChatOpenAI
from src.config import Config
from src.core.auth import get_azure_token_provider

def connect_to_azure_chat_model(json_mode: bool = True):
    """Connect to Azure OpenAI Chat Model.

    - json_mode=True  -> enforce structured JSON output (response_format=json_object)
    - json_mode=False -> free-form text (used for narrative re-render)
    """
    try:
        token_provider = get_azure_token_provider()

        model_kwargs = {}
        if json_mode:
            model_kwargs["response_format"] = {"type": "json_object"}

        model = AzureChatOpenAI(
            api_version=Config.AZURE_API_VERSION,
            azure_endpoint=Config.AZURE_ENDPOINT,
            azure_deployment=Config.AZURE_CHAT_DEPLOYMENT,
            azure_ad_token_provider=token_provider,
            temperature=0,
            model_kwargs=model_kwargs,
        )
        return model
    except Exception as e:
        print(f"Error connecting to Azure Chat: {e}")
        return None

def parse_model_response(ai_answer):
    """Safely parse model response into a Python object."""
    if ai_answer is None:
        return None

    content = getattr(ai_answer, "content", None)

    # If already a dict
    if isinstance(content, dict):
        return content

    # If string, try to parse JSON
    raw = content if content else str(ai_answer)
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Fallback
    return {"raw": raw}
