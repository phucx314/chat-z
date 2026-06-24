from openai import OpenAI
from ai.prompts import SYSTEM_PROMPT

def generate_reply(messages: list, model: str, api_key: str, base_url: str = None):
    """Abstraction for LLM provider calls."""
    try:
        client = OpenAI(api_key=api_key, base_url=base_url or None)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.8,
        )
        usage = response.usage
        print(f"DEBUG: Token Usage -> Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"AI Engine Error: {str(e)}")

import os


def _is_deepseek_base_url(base_url: str | None) -> bool:
    return bool(base_url and "api.deepseek.com" in base_url)

def get_embedding(text: str, api_key: str = None, base_url: str = None) -> list[float]:
    """Get vector embedding for a given text using OpenAI."""
    import os
    from openai import OpenAI
    
    # List of keys to try in order
    keys_to_try = []
    if api_key and not _is_deepseek_base_url(base_url):
        keys_to_try.append((api_key, base_url))
    
    # Environment fallbacks
    env_keys = [
        (os.getenv("OPENAI_API_KEY"), "https://api.openai.com/v1"),
        (os.getenv("MIMO_API_KEY"), "https://api.xiaomimimo.com/v1"),
        (os.getenv("DEDICATED_MIMO_API_KEY"), "https://token-plan-sgp.xiaomimimo.com/v1")
    ]
    
    for k, b in env_keys:
        if k and (k, b) not in keys_to_try:
            keys_to_try.append((k, b))

    last_error = "No keys available"
    models_to_try = ["text-embedding-3-small", "text-embedding-ada-002", "text-embedding-v1", "mimo-embedding"]
    
    for k, b in keys_to_try:
        client = OpenAI(api_key=k, base_url=b or None)
        for model in models_to_try:
            try:
                response = client.embeddings.create(input=text, model=model)
                return response.data[0].embedding
            except Exception as e:
                last_error = f"{model} failed: {str(e)}"
                continue
            
    raise Exception(f"Embedding failed (tried all keys and models): {last_error}")
