import os
import json
from dotenv import load_dotenv
from ai.models import PROVIDERS

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "config.json")
ENV_FILE    = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

load_dotenv(ENV_FILE, override=False)

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
    else:
        cfg = {"provider": "OpenAI", "base_url": "https://api.openai.com/v1",
               "model": "gpt-4o-mini", "api_key": "", "allow_interrupt": False}

    mimo_key      = os.getenv("MIMO_API_KEY", "")
    dedicated_key = os.getenv("DEDICATED_MIMO_API_KEY", "")
    openai_key    = os.getenv("OPENAI_API_KEY", "")

    if os.getenv("PROVIDER"):
        provider = os.getenv("PROVIDER")
    elif dedicated_key and not openai_key:
        provider = "MiMo (Token Plan — SG)"
        cfg["base_url"] = PROVIDERS["MiMo (Token Plan — SG)"]["base_url"]
        if not cfg.get("model") or cfg.get("model", "").startswith("gpt-"):
            cfg["model"] = "mimo-v2.5-pro"
    elif mimo_key and not openai_key:
        provider = "MiMo (Pay-As-You-Go)"
        cfg["base_url"] = PROVIDERS["MiMo (Pay-As-You-Go)"]["base_url"]
        if not cfg.get("model") or cfg.get("model", "").startswith("gpt-"):
            cfg["model"] = "mimo-v2.5-pro"
    elif openai_key and not mimo_key:
        provider = "OpenAI"
    else:
        provider = cfg.get("provider", "OpenAI")

    if "Token Plan" in provider:
        env_key = dedicated_key or mimo_key or openai_key
    elif "MiMo" in provider:
        env_key = mimo_key or dedicated_key or openai_key
    else:
        env_key = openai_key or mimo_key or dedicated_key

    cfg["provider"]     = provider
    cfg["_env_api_key"] = env_key
    cfg["_key_from_env"] = bool(env_key)
    if os.getenv("BASE_URL"):
        cfg["base_url"] = os.getenv("BASE_URL")
    if os.getenv("MODEL"):
        cfg["model"] = os.getenv("MODEL")
        
    cfg["allow_interrupt"] = cfg.get("allow_interrupt", False)
    return cfg

def get_effective_api_key(cfg: dict) -> str:
    return cfg.get("_env_api_key") or cfg.get("api_key", "")

def save_config(cfg: dict):
    to_save = {
        "provider": cfg.get("provider", "OpenAI"),
        "base_url": cfg.get("base_url", ""),
        "model":    cfg.get("model", "gpt-4o-mini"),
        "api_key":  cfg.get("api_key", ""),
        "allow_interrupt": cfg.get("allow_interrupt", False),
    }
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(to_save, f, indent=2)
