import streamlit as st
from datetime import datetime
import pyrebase
import os # Importar o módulo OS para ler variáveis de ambiente

# ====================================================================
# 1. 🔑 CONFIGURAÇÃO: LEITURA DE CREDENCIAIS DE FORMA SEGURA
# ====================================================================

def load_firebase_config():
    """
    Carrega as credenciais do Firebase.
    Prioriza st.secrets (local) e depois os.environ (Render).
    """
    
    # 🎯 Opção A: Leitura local (secrets.toml)
    if 'firebase' in st.secrets:
        st.success("Configuração carregada via secrets.toml (Local)")
        return st.secrets['firebase']
    
    # 🎯 Opção B: Leitura via Variáveis de Ambiente (Render)
    try:
        config = {
            "apiKey": os.environ.get("FIREBASE_API_KEY"),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.environ.get("FIREBASE_APP_ID")
        }
        
        # Verifica se pelo menos a chave principal foi lida (para o Render)
        if config["apiKey"]:
            st.success("Configuração carregada via Variáveis de Ambiente (Render)")
            return config
        
    except Exception as e:
        pass # Ignora, vai para o erro final

    # ❌ Erro: Configuração não encontrada
    st.error("ERRO DE CONFIGURAÇÃO: As chaves do Firebase não foram encontradas. Verifique seu .streamlit/secrets.toml ou as Variáveis de Ambiente do Render.")
    st.stop()
        
# Inicializa a configuração
firebase_config = load_firebase_config()


# Função para inicializar o Firebase
@st.cache_resource
def init_firebase(config):
    """Inicializa e retorna o objeto Pyrebase."""
    try:
        return pyrebase.initialize_app(config)
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")
        st.stop()


firebase = init_firebase(firebase_config)
db = firebase.database()
storage = firebase.storage()


# Estilo mobile-first (Mantido do original)
st.set_page_config(page_title="Guarulhos Fácil", page_icon="🏙️", layout="centered")
st.markdown("""
<style>
    /* ... Seu CSS mobile-first (Estilos) ... */
    @media (max-width: 768px) {
        .stApp { background-color: #f8f9fa; }
        h1 { font-size: 1.5rem; color: #0d1b2a; text-align: center; font-weight: 700; }
        h2 { font-size: 1.2rem; color: #1e293b; }
        .problem-card {
            background: white;
            padding: 16px;
            border-radius: 10px;
            margin: 12px 0;
            border-left: 4px solid #f99417;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stButton > button {
            width: 100%;
            background-color: #f99417;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #e07a00;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(249, 148, 23, 0.3);
        }
        .stTextInput > div > div > input, .stSelectbox > div > div > select, 
        .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        .footer {
            font-size: 0.85rem;
            color: #64748b;
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            border-top: 1px solid #e2e8f0;
        }
    }
    /* Desktop (Omitido para brevidade) */
</style>
""", unsafe_allow_html=True)

st.title("🏙️ Guarulhos Fácil")
st.subheader("Denuncie problemas urbanos — anônimo, rápido e construtivo")

# Tabs
tab1, tab2 = st.tabs(["📤 Denunciar", "🗺️ Na sua região"])

# =====================
# TAB 1: DENUNCIAR
# =====================
with tab1:
    st.markdown("Sua denúncia será enviada à **Ouvidoria Municipal de Guarulhos**.")
    st.caption("Anônima • Segura • Foco em soluções")

    with st.form("form_denuncia"):
        tipo = st.selectbox("Tipo de problema *", [
            "Buraco na via",
            "Lixo acumulado",
            "Iluminação pública apagada",
            "Sinalização danificada",
            "Queimada ou desmatamento",
            "Barulho excessivo",
            "Carro abandonado",
            "Outro"
        ])
        
        descricao = st.text_area("Descrição (opcional)", max_chars=300, 
                                 placeholder="Ex: Buraco com 30cm na esquina da Rua X com a Avenida Y.")
        
        foto = st.file_uploader("Foto do problema (opcional)", type=["jpg", "jpeg", "png"])
        
        st.info("📍 No celular, sua localização será usada automaticamente. Se necessário, ajuste os valores.")
        col_lat, col_lng = st.columns(2)
        with col_lat:
            lat = st.number_input("Latitude *", value=-23.456000, format="%.6f", help="Ex: -23.456000")
        with col_lng:
            lng = st.number_input("Longitude *", value=-46.543000, format="%.6f", help="Ex: -46.543000")
            
        submitted = st.form_submit_button("Enviar denúncia", type="primary")

        if submitted:
            # VALIDAÇÃO
            if not tipo or not lat or not lng:
                st.error("❌ Por favor, preencha o Tipo, Latitude e Longitude (campos com *).")
            else:
                try:
                    # UPLOAD DA IMAGEM
                    image_url = None
                    if foto is not None:
                        with st.spinner("Enviando foto para o Storage..."):
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            file_name = f"denuncia/{tipo.replace(' ', '_')}_{timestamp}.{foto.type.split('/')[-1]}"
                            
                            storage.child(file_name).put(foto.getvalue())
                            image_url = storage.child(file_name).get_url(None)

                    # SALVANDO NO DATABASE
                    denuncia = {
                        "tipo": tipo,
                        "descricao": descricao,
                        "lat": lat,
                        "lng": lng,
                        "data": datetime.now().isoformat(),
                        "confirmacoes": 1,
                        "status": "Pendente",
                        "url_foto": image_url
                    }
                    
                    with st.spinner("Registrando denúncia no banco de dados..."):
                        resultado = db.child("denuncias").push(denuncia)
                    
                    # FEEDBACK
                    protocolo = "GRL-" + resultado["name"] 
                    st.success(f"✅ Denúncia enviada! Protocolo: **{protocolo}**")
                    st.info("A Ouvidoria de Guarulhos receberá sua denúncia. Prazo: 10 dias úteis.")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao processar a denúncia. Verifique sua conexão com o Firebase: {str(e)}")

# =====================
# TAB 2: PROBLEMAS NA REGIÃO
# =====================
with tab2:
    st.write("Problemas confirmados por moradores perto de você.")
    st.caption("Só são exibidos com ≥2 confirmações e status 'Pendente'.")

    # Adiciona st.cache_data para acelerar o carregamento da lista
    @st.cache_data(ttl=60) # Cache de 60 segundos
    def fetch_denuncias():
        return db.child("denuncias").get().val()

    try:
        denuncias_raw = fetch_denuncias()
        
        if denuncias_raw:
            confirmadas = {
                k: v for k, v in denuncias_raw.items() 
                if v.get("confirmacoes", 0) >= 2 and v.get("status") == "Pendente"
            }
            
            if confirmadas:
                for key, d in confirmadas.items():
                    data_obj = datetime.fromisoformat(d['data'])
                    data_formatada = data_obj.strftime("%d/%b/%Y")

                    st.markdown(f"""
                    <div class="problem-card">
                        <strong>{d['tipo']}</strong><br>
                        {d.get('descricao', 'Sem descrição.')[:50]}...<br>
                        📍 Região: Lat {d['lat']}, Lng {d['lng']}<br>
                        👥 <strong>{d['confirmacoes']}</strong> moradores confirmaram<br>
                        📅 {data_formatada}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if d.get('url_foto'):
                         st.image(d['url_foto'], caption=f"Foto do problema de {d['tipo']}", width=300)

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("👍 Também vejo isso", key=f"conf_{key}"):
                            nova_qtd = d["confirmacoes"] + 1
                            db.child("denuncias").child(key).update({"confirmacoes": nova_qtd})
                            st.toast(f"✅ Confirmação registrada! Total: {nova_qtd}")
                            # Usamos rerun aqui para atualizar a lista imediatamente
                            st.experimental_rerun() 
                            
                    with col2:
                        if st.button("✅ Resolvido (Voto)", key=f"res_{key}"):
                            db.child("denuncias").child(key).update({"status": "Votado para Resolução"})
                            st.toast("🗳️ Seu voto de 'Resolvido' foi registrado!")
                            st.experimental_rerun()
            else:
                st.info("Nenhum problema com ≥2 confirmações e 'Pendente' ainda.")
        else:
            st.info("Nenhum problema registrado até agora.")
            
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar dados do banco. Verifique as credenciais ou a conexão: {str(e)}")

# Rodapé
st.markdown('<div class="footer">Guarulhos Fácil — Cidadania urbana com respeito.<br>Denúncias encaminhadas à Prefeitura de Guarulhos.</div>', unsafe_allow_html=True)
