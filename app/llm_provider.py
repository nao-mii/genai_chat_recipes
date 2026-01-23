from typing import Dict, Any
import yaml
import httpx
from openai import AzureOpenAI
from openai import APIConnectionError  # para tratar erro de conexão

def load_settings(path: str = "assets/settings.yml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_llm():
    """
    Cria um cliente Azure OpenAI sem proxy, com timeout explícito,
    e retorna uma função 'chat(messages)' que faz a chamada segura.
    """
    cfg = load_settings()
    
    credentials = cfg.get("credentials", {})
    llm_cfg = cfg.get("llm", {})

    api_key = credentials.get("azure_openai_api_key", "").strip()
    endpoint = credentials.get("azure_openai_endpoint", "").strip()
    api_version = credentials.get("azure_openai_api_version", "2024-02-15-preview")

    # Validação mínima (Azure não usa prefixo sk-)
    if not api_key or not endpoint:
        def chat(_messages):
            return (
                "⚠️ Credenciais do Azure OpenAI não encontradas ou inválidas.\n"
                "Verifique azure_openai_api_key e azure_openai_endpoint em assets/settings.yml."
            )
        return chat

    # ⚠️ Em Azure, 'model' = nome do DEPLOYMENT
    deployment_name = llm_cfg.get("deployment", "").strip()
    if not deployment_name:
        def chat(_messages):
            return (
                "⚠️ O nome do deployment do Azure OpenAI não foi definido.\n"
                "Configure llm.deployment em assets/settings.yml."
            )
        return chat

    temperature = llm_cfg.get("temperature")
    max_tokens = llm_cfg.get("max_tokens")

    # Cliente httpx SEM proxy, com timeout explícito
    http_client = httpx.Client(timeout=30.0)

    # Cliente Azure OpenAI
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        http_client=http_client,
    )

    def chat(messages):
        try:
            resp = client.chat.completions.create(
                model=deployment_name,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
            return resp.choices[0].message.content

        except APIConnectionError as e:
            return (
                "⚠️ Erro de conexão com o Azure OpenAI. "
                "Verifique sua rede, firewall ou VPN.\n"
                f"Detalhes: {e}"
            )

        except Exception as e:
            return f"⚠️ Erro ao chamar o Azure OpenAI: {e.__class__.__name__} — {e}"

    return chat