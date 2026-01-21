# 🍳 Visão Geral

GenAI Recipe Chat é um chatbot de receitas em Python + Streamlit que usa IA para sugerir receitas personalizadas com base no que o usuário tem em casa (modo despensa), nas restrições alimentares, no tempo disponível, no tipo de cozinha e no número de porções.
Por trás da interface simples, o app combina filtros determinísticos sobre um dataset local (JSON) e geração de texto via OpenAI para entregar resultados úteis e seguros.

# Principais recursos

1. 🎛️ Barra Lateral de preferências: porções, tempo máximo, cozinha, restrições (vegan/sem glúten etc.) e ingredientes disponíveis.
2. 🔎 Pré-filtragem local (JSON) para reduzir custo e aumentar relevância.
3. 💬 Respostas explicativas do LLM: passo a passo, substituições, variações e lista de compras.
4. 🇧🇷 Português-BR por padrão (ajustável).
5. 🧱 Arquitetura modular: UI (Streamlit) + Motor de Receita (filtros) + Orquestração LLM.


# 🗂️ Estrutura do Projeto
```text
genai_recipe_chat/
├─ assets/
│  └─ settings.yml           # credenciais e configurações
├─ data/
│  └─ recipes_sample.json      # dataset inicial pequeno (exemplos)
├─ app/
│  ├─ llm_provider.py        # cliente OpenAI + timeouts + tratamento de erro
│  ├─ recipe_engine.py       # filtros: despensa, restrições, tempo, ranking
│  └─ prompts.py             # prompts do sistema/usuário
├─ streamlit_app.py          # interface do chatbot
├─ requirements.txt          # versões das bibliotecas python
└─ README.md
```

# 🔧 Requisitos

Python 3.9+ (recomendado 3.10/3.11).
Chave de API do OpenAI.

# ⚙️ Instalação

Windows / PowerShell
``` text
PowerShellcd C:\caminho\para\genai_recipe_chatpython -m venv venv.\venv\Scripts\activatepython -m pip install --upgrade pippip install -r requirements.txtMostrar mais linhas
```
macOS / Linux
```text
Shellcd ~/genai_recipe_chatpython3 -m venv venvsource venv/bin/activatepython3 -m pip install --upgrade pippip install -r requirements.txtMostrar mais linhas
requirements.txt (recomendado):
Plain Textstreamlit==1.40.0openai==1.52.2httpx==0.27.2pyyaml==6.0.2pydantic==2.9.2python-dotenv==1.0.1pandas==2.2.3Mostrar mais linhas
```

# 🔐 Configuração de Credenciais
Edite assets/settings.yml:
```text
llm:
    provider: "openai"
    model: "gpt-4o-mini"       # ajuste conforme conta/deploy
    temperature: 0.3
    max_tokens: 1000
credentials:
    openai_api_key: "sk-COLOQUE_SUA_CHAVE_AQUI"
```
OpenAI: gere a chave em https://platform.openai.com/account/api-keys

# ▶️ Como Executar
PowerShell
``` text
# no mesmo venvpython -m streamlit run streamlit_app.pyMostrar mais linhas
```
O Streamlit abrirá o app em http://localhost:8501.

# 🧪 Teste Rápido de Conexão (Isolado)
Se quiser testar a API antes de iniciar o app:
```text
python - << 'PY'
from openai import OpenAI
import httpx
client = OpenAI(api_key="sk-...", http_client=httpx.Client(timeout=30.0))
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Diga 'ok'"}],
    max_tokens=5)
print(r.choices[0].message.content)
PY
```
# 🚑 Solução de Problemas (FAQ)
## “streamlit não reconhecido”
Ative o venv e chame com python -m:
``` text
.\venv\Scripts\activate
python -m streamlit run streamlit_app.py
```

## TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
Fixe o httpx:
```text
pip install "httpx==0.27.2"Mostrar mais linhas
```

## APIConnectionError: Connection error
- Verifique sua internet.
- Tente curl https://api.openai.com/v1/models.
- Se abrir página Zscaler/antivírus (status 200 com HTML), sua rede está interceptando/bloqueando a OpenAI.
    - Soluções:
        - Teste 3G/5G do celular.


# 🛡️ Boas Práticas

- Não comitar chaves (settings.yml no .gitignore se for repositório público).
- Limite max_tokens e use modelos econômicos para controlar custo.
- Logue uso (latência/custos) — sem dados sensíveis.
- Alerte sobre alergênicos e substituições seguras no SYSTEM_PROMPT.
