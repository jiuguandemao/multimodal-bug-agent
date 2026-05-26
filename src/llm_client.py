import os
from dataclasses import dataclass
from typing import List, Optional

import requests
from dotenv import load_dotenv


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 60
    thinking: str = "disabled"
    reasoning_effort: str = "high"


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config

    @classmethod
    def from_env(cls) -> "LLMClient":
        load_dotenv()
        provider = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()
        api_key = (
            os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        )
        default_base = "https://api.deepseek.com" if provider == "deepseek" else os.getenv("LLM_API_BASE", "")
        base_url = os.getenv("LLM_API_BASE", default_base).rstrip("/")
        model = os.getenv("LLM_MODEL", "deepseek-v4-flash" if provider == "deepseek" else "gpt-4o-mini")
        timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        thinking = os.getenv("DEEPSEEK_THINKING", "disabled")
        reasoning_effort = os.getenv("DEEPSEEK_REASONING_EFFORT", "high")
        return cls(LLMConfig(provider, api_key, base_url, model, timeout, thinking, reasoning_effort))

    def is_configured(self) -> bool:
        return bool(self.config.api_key and self.config.base_url and self.config.model)

    def chat(self, messages: List[dict], max_tokens: int = 1200) -> Optional[str]:
        if not self.is_configured():
            return None

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
        }
        if self.config.provider == "deepseek":
            payload["thinking"] = {"type": self.config.thinking}
            if self.config.thinking == "enabled":
                payload["reasoning_effort"] = self.config.reasoning_effort

        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def try_llm_enhance(messages: List[dict]) -> tuple:
    client = LLMClient.from_env()
    if not client.is_configured():
        return client.config, "skipped", ""
    try:
        content = client.chat(messages)
        return client.config, "ok", content or ""
    except Exception as exc:
        return client.config, f"error: {exc}", ""
