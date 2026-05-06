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
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"AI Engine Error: {str(e)}")
