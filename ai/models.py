PROVIDERS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "MiMo (Pay-As-You-Go)": {
        "base_url": "https://api.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — SG)": {
        "base_url": "https://token-plan-sgp.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — EU)": {
        "base_url": "https://token-plan-ams.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — CN)": {
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
}
