"""Model client.

Microsoft Foundry serves OpenAI models (like gpt-5-mini) through an
Azure-OpenAI-compatible endpoint, so the standard `openai` SDK works. If you
later switch to a Claude or MAI model in Foundry, only this file changes.
"""

from openai import OpenAI

from . import config

_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        # Foundry's v1 endpoint is OpenAI-compatible, so the plain OpenAI
        # client works: point base_url at /openai/v1/ and pass the key.
        _client = OpenAI(
            api_key=config.AZURE_API_KEY,
            base_url=config.AZURE_BASE_URL,
        )
    return _client
