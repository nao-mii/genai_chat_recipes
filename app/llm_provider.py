from typing import Dict, Any
import yaml
import httpx
from openai import OpenAI
from openai import APIConnectionError  # para tratar erro de conexão

def load_settings(path: str = "assets/settings.yml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_llm():
    """
    Cria um cliente OpenAI sem proxy, com timeout explícito,
    e retorna uma função 'chat(messages)' que faz a chamada segura.
    """
    cfg = load_settings()
    api_key = cfg["credentials"].get("openai_api_key", "").strip()
    if not api_key or not api_key.startswith(("sk-", "rk-")):
        # Mensagem amigável caso a chave não esteja definida
        def chat(_messages):
            return "⚠️ A chave de API do OpenAI não foi encontrada ou é inválida em assets/settings.yml."
        return chat

    model = cfg["llm"].get("model", "gpt-4o-mini")
    temperature = float(cfg["llm"].get("temperature", 0.3))
    max_tokens = int(cfg["llm"].get("max_tokens", 800))

    # Cliente httpx SEM proxies, com timeout explícito.
    http_client = httpx.Client(timeout=30.0)

    # Cliente OpenAI (SDK nova)
    client = OpenAI(api_key=api_key, http_client=http_client)

    def chat(messages):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=messages,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except APIConnectionError as e:
            return (
                "⚠️ Erro de conexão com a API OpenAI. "
                "Verifique sua internet, firewall/antivírus e tente novamente.\n"
                f"Detalhes: {e}"
            )
        except Exception as e:
            # Mostra erro genérico; útil para debugging inicial
            return f"⚠️ Erro ao chamar a API OpenAI: {e.__class__.__name__} — {e}"

    return chat
