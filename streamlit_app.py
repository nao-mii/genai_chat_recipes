import streamlit as st
from app.llm_provider import get_llm
from app.recipe_engine import load_local_recipes, filter_candidates, build_llm_messages
from app.prompts import SYSTEM_PROMPT, USER_GUIDANCE

# ===== Config e título
st.set_page_config(page_title="GenAI Recipe Chat", page_icon="🍳", layout="centered")
st.title("🍳 GenAI Recipe Chat")
st.caption("Assistente de receitas com IA — PT-BR")

# ===== Preferências (sidebar)
with st.sidebar:
    st.subheader("Preferências")
    servings = st.number_input("Porções", min_value=1, max_value=20, value=2)
    time_limit = st.number_input("Tempo máx. (min)", min_value=0, max_value=240, value=30)
    cuisine = st.text_input("Cozinha (opcional)", value="")
    dietary = st.multiselect("Restrições", ["vegan", "vegetariano", "sem_gluten", "sem_lactose", "low_carb"])
    pantry_text = st.text_area("Ingredientes disponíveis (separe por vírgula)", "frango, limão, alho, azeite")
    pantry = [p.strip() for p in pantry_text.split(",") if p.strip()]

    # === Painel de diagnóstico
    with st.expander("🔍 Diagnóstico rápido"):
        import os, sys
        st.write("**Versões**")
        try:
            import openai, httpx
            st.code(f"openai={openai.__version__} | httpx={httpx.__version__} | python={sys.version.split()[0]}")
        except Exception as e:
            st.warning(f"Não consegui ler versões: {e}")

        st.write("**Chaves & ambiente**")
        # Não mostramos a chave por segurança; só um status
        api_key_present = bool(os.environ.get("OPENAI_API_KEY"))  # pode ou não estar via env
        st.write(f"OPENAI_API_KEY (env) definido? {'✅' if api_key_present else '❌'}")
        st.write("Se você usa settings.yml, a verificação de chave será feita ao criar o cliente.")

# ===== Estado de conversa
if "history" not in st.session_state:
    st.session_state.history = []

# ===== Cria cliente LLM e carrega receitas
# get_llm() já valida a chave via settings.yml e retorna uma função chat(...)
chat = get_llm()
local_recipes = load_local_recipes()

# ===== Caixa de chat
user_input = st.chat_input("O que você quer cozinhar hoje? (ex.: 'jantar rápido sem lactose')")

if user_input:
    # guarda histórico do usuário
    st.session_state.history.append({"role": "user", "content": user_input})

    # seleciona candidatos do dataset local
    candidates = filter_candidates(
        recipes=local_recipes,
        pantry=pantry,
        dietary=dietary,
        time_limit=int(time_limit) if time_limit else None,
        cuisine=cuisine if cuisine else None
    )

    context = dict(
        pantry=", ".join(pantry),
        dietary=", ".join(dietary) or "nenhuma",
        time_limit=time_limit or "sem limite",
        servings=servings,
        cuisine=cuisine or "indiferente"
    )

    messages = build_llm_messages(SYSTEM_PROMPT, USER_GUIDANCE, context, candidates)
    # adiciona um pouco de memória (sem exagero pra não sair caro)
    messages += st.session_state.history[-5:]

    # === Chamada protegida ao LLM
    try:
        response = chat(messages)
    except Exception as e:
        # Se sua função chat já trata exceções e retorna string, isso provavelmente não será chamado.
        response = f"⚠️ Erro inesperado ao chamar o LLM: {e.__class__.__name__} — {e}"

    st.session_state.history.append({"role": "assistant", "content": response})

# ===== Renderiza histórico
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])