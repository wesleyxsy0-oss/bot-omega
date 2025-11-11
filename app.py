import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURAÇÃO DO FIREBASE ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Firebase: {e}")
        st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Comunica Sua Cidade",
    page_icon="📢",
    layout="centered"
)

# --- ESTILO CSS ---
st.markdown("""
<style>
    .menu-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .menu-item:hover {
        transform: scale(1.05);
    }
    .menu-item img {
        width: 50px;
        height: 50px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA CARREGAR ÍCONES DA PASTA STATIC ---
def load_icon(path):
    try:
        with open(path, 'rb') as f:
            return f"data:image/png;base64,{f.read().hex()}"
    except Exception as e:
        st.warning(f"⚠️ Ícone não encontrado: {path}")
        return "https://via.placeholder.com/50?text=Icon"

# --- NAVEGAÇÃO ---
if "page" not in st.session_state:
    st.session_state.page = "inicio"

# --- CABEÇALHO ---
st.image("https://via.placeholder.com/300x100?text=Comunica+Sua+Cidade", use_column_width=True)
st.markdown("<h3 style='text-align: center;'>Sua voz constrói a cidade</h3>", unsafe_allow_html=True)

# --- PAINEL RÁPIDO (4 BOTÕES) ---
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if st.button("", key="btn_comunicar"):
        st.session_state.page = "comunicar"
    st.markdown(f"""
    <div class="menu-item">
        <img src="{load_icon('static/icone_comunicar.png')}" alt="Comunicar Problema">
        <p>Comunicar Problema</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("", key="btn_demandas"):
        st.session_state.page = "demandas"
    st.markdown(f"""
    <div class="menu-item">
        <img src="{load_icon('static/icone_demandas.png')}" alt="Minhas Demandas">
        <p>Minhas Demandas</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("", key="btn_mapa"):
        st.session_state.page = "mapa"
    st.markdown(f"""
    <div class="menu-item">
        <img src="{load_icon('static/icone_mapa.png')}" alt="Mapa de Ocorrências">
        <p>Mapa de Ocorrências</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if st.button("", key="btn_servicos"):
        st.session_state.page = "servicos"
    st.markdown(f"""
    <div class="menu-item">
        <img src="{load_icon('static/icone_servicos.png')}" alt="Serviços da Cidade">
        <p>Serviços da Cidade</p>
    </div>
    """, unsafe_allow_html=True)

# --- CONTEÚDO DAS PÁGINAS ---
if st.session_state.page == "inicio":
    st.info("Selecione uma opção acima para começar.")

elif st.session_state.page == "comunicar":
    st.header("📢 Comunicar Problema")
    with st.form("form_denuncia"):
        local = st.text_input("📍 Onde está o problema?")
        categoria = st.selectbox("🔧 Tipo de problema", ["Buraco", "Lixo", "Iluminação", "Outro"])
        descricao = st.text_area("📝 Descrição")
        enviado = st.form_submit_button("Enviar")
    
    if enviado and local and descricao:
        try:
            db.collection("denuncias").add({
                "categoria": categoria,
                "descricao": descricao,
                "local": local,
                "data": firestore.SERVER_TIMESTAMP
            })
            st.success("✅ Enviado! Obrigado por ajudar.")
        except Exception as e:
            st.error(f"Erro: {e}")

elif st.session_state.page == "demandas":
    st.header("📋 Minhas Demandas")
    st.info("Aqui você verá suas denúncias enviadas.")

elif st.session_state.page == "mapa":
    st.header("🗺️ Mapa de Ocorrências")
    st.map()
    st.info("Em breve: mapa interativo com todas as denúncias!")

elif st.session_state.page == "servicos":
    st.header("⚙️ Serviços da Cidade")
    st.write("Contatos úteis:")
    st.markdown("- **Prefeitura:** (XX) XXXX-XXXX")
    st.markdown("- **Limpeza Urbana:** (XX) XXXX-XXXX")
    st.markdown("- **Iluminação Pública:** (XX) XXXX-XXXX")
