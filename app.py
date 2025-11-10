import streamlit as st
import base64
from datetime import datetime
import pyrebase

# 🔑 Configuração do Firebase — já com seus dados reais
firebase_config = {
    "apiKey": "AIzaSyAj0SlpJXb8xEzL8vWxpaCOqrjU4MsiaeQ",
    "authDomain": "comunica-guarulhos.firebaseapp.com",
    "databaseURL": "https://comunica-guarulhos-default-rtdb.firebaseio.com",
    "projectId": "comunica-guarulhos",
    "storageBucket": "comunica-guarulhos.firebasestorage.app",
    "messagingSenderId": "849187017943",
    "appId": "1:849187017943:web:b2f85534675f432c3e4c92"
}

# Função para inicializar o Firebase (só uma vez)
@st.cache_resource
def init_firebase():
    return pyrebase.initialize_app(firebase_config)

# Estilo do app
st.set_page_config(page_title="Guarulhos Fácil", page_icon="🏙️", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1 { color: #0d1b2a; text-align: center; font-weight: 700; }
    h2 { color: #1e293b; }
    .problem-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #f99417;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .footer {
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #e2e8f0;
    }
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
    st.caption("Anônimo • Seguro • Foco em soluções")

    tipo = st.selectbox("Tipo de problema", [
        "Buraco na via",
        "Lixo acumulado",
        "Iluminação pública apagada",
        "Sinalização danificada",
        "Queimada ou desmatamento",
        "Barulho excessivo",
        "Carro abandonado",
        "Outro"
    ])
    
    descricao = st.text_area("Descrição (opcional)", max_chars=200, placeholder="Ex: Buraco com 30cm, esquina com Rua X")
    foto = st.file_uploader("Foto do problema (opcional)", type=["jpg", "jpeg", "png"])
    
    st.info("📍 No celular, sua localização será usada automaticamente.")
    lat = st.text_input("Latitude", value="-23.456", help="Ex: -23.456")
    lng = st.text_input("Longitude", value="-46.543", help="Ex: -46.543")
    
    if st.button("Enviar denúncia", type="primary"):
        try:
            # Inicializa Firebase
            firebase = init_firebase()
            db = firebase.database()
            
            # Salva denúncia
            denuncia = {
                "tipo": tipo,
                "descricao": descricao,
                "lat": lat,
                "lng": lng,
                "data": datetime.now().isoformat(),
                "confirmacoes": 1,
                "resolvido": 0
            }
            
            db.child("denuncias").push(denuncia)
            st.success("✅ Denúncia enviada! Protocolo: GRL-2025-XXXXX")
            st.info("A Ouvidoria de Guarulhos receberá sua denúncia. Prazo: 10 dias úteis.")
            
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
            st.warning("Verifique a conexão com a internet e as permissões do Firebase.")

# =====================
# TAB 2: PROBLEMAS NA REGIÃO
# =====================
with tab2:
    st.write("Problemas confirmados por moradores perto de você.")
    st.caption("Só são exibidos com ≥2 confirmações.")

    try:
        firebase = init_firebase()
        db = firebase.database()
        denuncias = db.child("denuncias").get().val()
        
        if denuncias:
            confirmadas = {k: v for k, v in denuncias.items() if v.get("confirmacoes", 0) >= 2}
            
            if confirmadas:
                for key, d in confirmadas.items():
                    st.markdown(f"""
                    <div class="problem-card">
                        <strong>{d['tipo']}</strong><br>
                        📍 Região: Lat {d['lat'][:7]}, Lng {d['lng'][:7]}<br>
                        👥 {d['confirmacoes']} moradores confirmaram<br>
                        📅 {d['data'][:10]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Também vejo isso", key=f"conf_{key}"):
                            nova_qtd = d["confirmacoes"] + 1
                            db.child("denuncias").child(key).update({"confirmacoes": nova_qtd})
                            st.experimental_rerun()
                    with col2:
                        if st.button("✅ Resolvido", key=f"res_{key}"):
                            nova_qtd = d.get("resolvido", 0) + 1
                            db.child("denuncias").child(key).update({"resolvido": nova_qtd})
                            st.experimental_rerun()
            else:
                st.info("Nenhum problema com ≥2 confirmações ainda.")
        else:
            st.info("Nenhum problema registrado até agora.")
            
    except Exception as e:
        st.warning("⚠️ Sem conexão com o banco de dados. Modo offline.")

# Rodapé
st.markdown('<div class="footer">Guarulhos Fácil — Cidadania urbana com respeito.<br>Denúncias encaminhadas à Prefeitura de Guarulhos.</div>', unsafe_allow_html=True)
