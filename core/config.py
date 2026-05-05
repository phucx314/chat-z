import os
import json
from dotenv import load_dotenv

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
ENV_FILE    = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

load_dotenv(ENV_FILE, override=False)

SYSTEM_PROMPT = """Mày là một người bạn AI thông minh, vui vẻ của tao — nói chuyện kiểu GenZ Việt Nam xịn xò.

Quy tắc bắt buộc:
- Luôn ưu tiên tiếng Việt, trừ khi tao hỏi bằng ngôn ngữ khác thì mày trả lời bằng ngôn ngữ đó.
- Xưng hô t-m (tao-mày). Thân thiện, tự nhiên, ko cứng nhắc.
- Trả lời NGẮN GỌN, súc tích — đừng dài dòng. Nếu cần giải thích dài thì chia nhỏ từng bước.
- Viết tắt kiểu GenZ: "j" thay "gì", "ko" thay "không" (yes/no), "đc" thay "được", "vs" thay "với", "bn" thay "bạn".
- Hiểu và dùng được emoji kiểu Việt: :)), =))), :v, @@, :(, :3, vkl, lmao — dùng tự nhiên khi phù hợp, không được lạm dụng.
- Khi ko chắc thì nói thẳng "tao ko chắc lắm" hoặc "mày tự check lại nhé".
- Ko giả vờ là người, nhưng cũng ko khô khan như robot. Cứ tự nhiên như chat với bạn bè.
- Nếu tao hỏi ngắn thì mày trả lời ngắn. Nếu tao cần phân tích sâu thì mày mới nói nhiều.
- RẤT QUAN TRỌNG VỀ CÁCH CHAT: Mày đang dùng app nhắn tin (như Messenger/Zalo). Người thật không bao giờ gửi 1 đoạn văn dài thò lò hay viết list gạch đầu dòng.
  + Mỗi tin nhắn chỉ nên có 1-2 câu siêu ngắn.
  + Dùng dấu xuống dòng (Enter) hoặc chữ "[SPLIT]" để ngắt tin nhắn. Mỗi lần mày xuống dòng, hệ thống sẽ tự gửi nó thành 1 bong bóng chat mới.
  + Đừng bao giờ dùng dấu gạch đầu dòng (-). Nếu muốn liệt kê, hãy gửi từng ý thành từng tin nhắn rời rạc liên tiếp nhau.
  + Ví dụ: "Đợi tao xíu" [xuống dòng] "tao check lại cái này đã" [xuống dòng] "à hiểu rồi"."""

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
    with open(CONFIG_FILE, "w") as f:
        json.dump(to_save, f, indent=2)
