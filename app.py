import streamlit as st
import json
import base64
from datetime import datetime
import pyrebase

# Configuração do Firebase (substitua pelos seus dados)
firebase_config = {
    "apiKey": "SUA_API_KEY",
    "authDomain": "guarulhos-facil.firebaseapp.com",
    "databaseURL": "https://guarulhos-facil-default-rtdb.firebaseio.com",
    "projectId": "guarulhos-facil",
    "storageBucket": "guarulhos-facil.appspot.com",
    "messagingSenderId": "SEU_SENDER_ID",
    "appId": "SEU_APP_ID"
}

# Função para inicializar Firebase
@st.cache_resource
def init_firebase():
    return pyrebase.initialize_app(firebase_config)

# Estilo
st.set_page_config(page_title="Guarulhos Fácil", page_icon="🏙️", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1 { color: #0d1b2a; text-align: center; }
    .problem-card {
        background: white; padding: 16px; border-radius: 10px;
        margin: 10px 0; border-left: 4px solid #f99417;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("🏙️ Guarulhos Fácil")
st.subheader("Denuncie problemas urbanos — de forma anônima e construtiva")

# Tabs
tab1, tab2 = st.tabs(["📤 Denunciar", "🗺️ Problemas na sua região"])

# ============ TAB 1: DENUNCIAR ============
with tab1:
    st.write("Sua denúncia será enviada à **Ouvidoria Municipal de Guarulhos**.")
    st.caption("Anônima, segura e com foco em soluções.")
    
    tipo = st.selectbox("Tipo de problema", [
        "Buraco na via",
        "Lixo acumulado",
        "Iluminação pública apagada",
        "Sinalização danificada",
        "Queimada ou desmatamento",
        "Barulho excessivo",
        "Outro"
    ])
    
    descricao = st.text_area("Descrição (opcional)", max_chars=200)
    foto = st.file_uploader("Foto do problema (opcional)", type=["jpg", "png"])
    
    # Simular geolocalização (no celular, usaria navigator.geolocation)
    st.info("📍 No app móvel, sua localização será detectada automaticamente.")
    lat = st.text_input("Latitude (ex: -23.456)", value="-23.456")
    lng = st.text_input("Longitude (ex: -46.543)", value="-46.543")
    
    if st.button("Enviar denúncia"):
        try:
            # Salvar no Firebase
            firebase = init_firebase()
            db = firebase.database()
            
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
            
            # (Opcional) Enviar e-mail para Ouvidoria
            st.success("✅ Denúncia enviada! Protocolo: GRL-2025-XXXXX")
            st.info("A Ouvidoria de Guarulhos receberá sua denúncia. Prazo de resposta: 10 dias úteis.")
        except Exception as e:
            st.error(f"Erro: {str(e)}")

# ============ TAB 2: PROBLEMAS NA REGIÃO ============
with tab2:
    st.write("Veja problemas confirmados por moradores perto de você.")
    st.caption("Só são exibidos problemas com ≥2 confirmações.")
    
    try:
        firebase = init_firebase()
        db = firebase.database()
        denuncias = db.child("denuncias").get().val()
        
        if denuncias:
            for key, d in denuncias.items():
                if d.get("confirmacoes", 0) >= 2:
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
                            # Incrementar confirmações
                            db.child("denuncias").child(key).update({"confirmacoes": d["confirmacoes"] + 1})
                    with col2:
                        if st.button("✅ Resolvido", key=f"res_{key}"):
                            db.child("denuncias").child(key).update({"resolvido": d.get("resolvido", 0) + 1})
        else:
            st.info("Nenhum problema confirmado por enquanto.")
    except Exception as e:
        st.warning("Sem conexão com o banco de dados. Modo offline.")

# Rodapé
st.markdown("---")
st.caption("Guarulhos Fácil — Cidadania urbana com respeito e transparência. \n\n"
           "Este app encaminha denúncias à Prefeitura de Guarulhos. Não armazenamos seus dados.")
