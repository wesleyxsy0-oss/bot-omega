import streamlit as st
import pyrebase
from datetime import datetime
import base64
import json
import uuid

# =======================================================
# 🔑 1. CONFIGURAÇÃO DE SEGURANÇA E FIREBASE
# =======================================================
# !!! IMPORTANTE: NUNCA DEIXE SUAS CHAVES AQUI. USE st.secrets !!!
try:
    # Tentativa de carregar as credenciais de forma segura (Recomendado para deploy)
    firebase_config = {
        "apiKey": st.secrets["firebase"]["api_key"],
        "authDomain": st.secrets["firebase"]["auth_domain"],
        "databaseURL": st.secrets["firebase"]["database_url"],
        "projectId": st.secrets["firebase"]["project_id"],
        "storageBucket": st.secrets["firebase"]["storage_bucket"],
        "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
        "appId": st.secrets["firebase"]["app_id"],
    }
except:
    # Se você estiver rodando localmente (SUBSTITUA PELAS SUAS CREDENCIAIS REAIS)
    st.warning("⚠️ Usando credenciais HARDCODED. Configure st.secrets no deploy!")
    firebase_config = {
        "apiKey": "AIzaSyAj0SlpJXb8xEzL8vWxpaCOqrjU4MsiaeQ", # SUBSTITUA PELA SUA CHAVE
        "authDomain": "comunica-guarulhos.firebaseapp.com",
        "databaseURL": "https://comunica-guarulhos-default-rtdb.firebaseio.com",
        "projectId": "comunica-guarulhos",
        "storageBucket": "comunica-guarulhos.appspot.com", # Geralmente é appspot.com
        "messagingSenderId": "849187017943",
        "appId": "1:849187017943:web:b2f85534675f432c3e4c92"
    }


# Inicializa o Firebase
@st.cache_resource
def init_firebase():
    return pyrebase.initialize_app(firebase_config)

# =======================================================
# ⚙️ 2. ESTILOS (Incluindo os Ícones-Botão)
# =======================================================
# Baseado na sua intenção, usaremos o 'session_state' para gerenciar as telas
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# HTML & CSS para Mobile-First e Botões de Ícones
st.set_page_config(page_title="Comunica Guarulhos", page_icon="📢", layout="centered")

st.markdown(f"""
<style>
    /* Estilos Básicos do Streamlit e Fundo */
    .stApp {{ background-color: #f8f9fa; }}
    /* Adiciona espaço para a barra de navegação fixa */
    .main {{ padding-bottom: 80px; }} 
    h1, h2, h3 {{ color: #0d1b2a; text-align: center; }}
    
    /* -------------------------------------- */
    /* BARRA DE NAVEGAÇÃO INFERIOR FIXA */
    /* -------------------------------------- */
    .footer-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: white;
        box-shadow: 0 -4px 6px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 1000;
        padding: 0 5px;
    }}
    /* Estilo padrão do botão de navegação */
    .nav-button {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 5px;
        color: #6c757d;
        font-size: 0.75rem;
        font-weight: 500;
        text-decoration: none;
        transition: color 0.2s, background-color 0.2s;
        border: none;
        background: none;
        cursor: pointer;
        outline: none;
    }}
    /* Efeito hover e estado ativo */
    .nav-button:hover, .nav-button.active {{
        color: #f99417; /* Cor de destaque */
    }}
    .nav-button img {{
        width: 24px;
        height: 24px;
        margin-bottom: 3px;
    }}
    
    /* Botão Flutuante Central (Nova Comunicação) */
    .fab-container {{
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1001;
    }}
    .fab-button {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #2a9d8f; /* Uma cor de ação */
        color: white;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        transition: background-color 0.2s;
        cursor: pointer;
    }}
    .fab-button:hover {{
        background-color: #218376;
    }}
    /* Cor de destaque para o botão ativo */
    .active-fab {{
        background-color: #f99417 !important; 
    }}
    
    /* Estilo para as cards de problemas */
    .problem-card {{
        background: white;
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #f99417;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .footer {{
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #e2e8f0;
    }}
    /* Esconde o menu Streamlit nativo para uma aparência mais limpa */
    #MainMenu, footer {{visibility: hidden;}}
    
</style>
""", unsafe_allow_html=True)

# Define os URLs externos para os botões de "Mais"
OUVIDORIA_URL = "https://www.guarulhos.sp.gov.br/ouvidoria-geral-do-municipio"
CAMARA_URL = "https://www.camaraguarulhos.sp.gov.br/"
SERVICOS_URL = "https://portal.guarulhos.sp.gov.br/servicos"

# =======================================================
# 🖼️ 3. Funções de Layout / Páginas
# =======================================================
# Nota: Os caminhos 'src' dos ícones esperam que eles estejam na pasta 'static/images'
# e o Streamlit acessa arquivos estáticos pela raiz.

def main_header():
    # Caminho corrigido para icone_logo.png
    st.markdown(f"""
        <h1 style="text-align: left; margin-top: 0;">
            <img src='icone_logo.png' style='height: 30px; vertical-align: middle; margin-right: 10px;'>
            Comunica Guarulhos
        </h1>
    """, unsafe_allow_html=True)
    st.subheader("Sua voz constrói a cidade.")
    st.write("---")


def render_home_page():
    main_header()
    
    # ----------------------------------------------------
    # Atalhos para Serviços 
    # ----------------------------------------------------
    st.subheader("Acesso Rápido")
    col1, col2 = st.columns(2)
    
    with col1:
        # Usa o ícone icone_ouvidoria.png
        st.markdown(f"""
            <a href="{OUVIDORIA_URL}" target="_blank" class="nav-button" style="width: 100%; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 10px;">
                <img src="icone_ouvidoria.png" alt="Ouvidoria">
                <span>Ouvidoria</span>
            </a>
        """, unsafe_allow_html=True)
    with col2:
        # Usa o ícone icone_camara.png
        st.markdown(f"""
            <a href="{CAMARA_URL}" target="_blank" class="nav-button" style="width: 100%; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 10px;">
                <img src="icone_camara.png" alt="Câmara">
                <span>Câmara Mun.</span>
            </a>
        """, unsafe_allow_html=True)
    
    # Usa o ícone icone_servicos.png
    st.markdown(f"""
        <a href="{SERVICOS_URL}" target="_blank" class="nav-button" style="width: 99%; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px;">
            <img src="icone_servicos.png" alt="Serviços Online">
            <span>Serviços Online da Prefeitura</span>
        </a>
    """, unsafe_allow_html=True)

    # Exemplo de Estatísticas
    st.info("✅ *345* demandas resolvidas em 2025.")
    st.warning("🔥 *12* problemas de Iluminação em aberto.")


def render_denuncia_page():
    firebase = init_firebase()
    db = firebase.database()
    storage = firebase.storage()
    
    st.title("📢 Nova Comunicação")
    st.markdown("Relate o problema para a Ouvidoria Municipal de Guarulhos.")
    st.caption("Anonimato garantido.")

    # CATEGORIZAÇÃO 
    tipo = st.selectbox("1. Tipo de Problema", [
        "Buraco na Via / Asfalto",
        "Lixo e Entulho Acumulado",
        "Iluminação Pública (Apagada/Queimada)",
        "Drenagem / Esgoto / Bueros",
        "Sinalização de Trânsito",
        "Árvore Caída / Poda",
        "Carro Abandonado",
        "Barulho / Poluição Sonora",
        "Outro / Geral"
    ], help="Selecione a categoria para direcionar o órgão correto.")

    # LOCALIZAÇÃO (Com placeholders mais claros)
    st.subheader("2. Localização")
    st.info("💡 *DICA:* Se estiver no celular, o app tentará preencher a latitude/longitude.")
    lat = st.text_input("Latitude", placeholder="Ex: -23.456", help="Atenção: A precisão é crucial.")
    lng = st.text_input("Longitude", placeholder="Ex: -46.543")

    # DESCRIÇÃO E FOTO
    st.subheader("3. Detalhes (Opcional)")
    descricao = st.text_area("Descrição do Problema", max_chars=300, placeholder="Ex: Buraco grande na esquina da Rua X com a Avenida Y, em frente à escola.")
    foto_upload = st.file_uploader("Foto (Opcional)", type=["jpg", "jpeg", "png"])
    
    if st.button("Enviar Comunicação", type="primary"):
        if not lat or not lng:
            st.error("❌ Por favor, informe a Latitude e a Longitude.")
            return

        # ----------------------------------------------------
        # Lógica de Upload de Foto para Firebase Storage 
        # ----------------------------------------------------
        foto_url = ""
        if foto_upload is not None:
            try:
                # Gera um nome de arquivo único
                filename = f"denuncias/{uuid.uuid4()}.{foto_upload.name.split('.')[-1]}"
                
                # O Pyrebase precisa do arquivo em bytes/stream
                storage.child(filename).put(foto_upload.read())
                
                # Pega a URL pública (usando a função de download)
                foto_url = storage.child(filename).get_url(None)
                
            except Exception as e:
                st.warning(f"⚠️ Erro ao fazer upload da foto. A denúncia será enviada sem ela. Erro: {str(e)}")


        # ----------------------------------------------------
        # Lógica de Envio para Realtime Database 
        # ----------------------------------------------------
        denuncia = {
            "tipo": tipo,
            "descricao": descricao,
            "lat": lat,
            "lng": lng,
            "data": datetime.now().isoformat(),
            "status": "Enviada / Em Análise", # NOVO CAMPO DE STATUS!
            "foto_url": foto_url,
            "confirmacoes": 1,
            "protocolo": f"GRL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        }
        
        # O push retorna um objeto com o ID da nova entrada
        result = db.child("denuncias").push(denuncia)
        
        # Salva o ID da denúncia para o usuário ver no histórico
        if 'user_denuncias_keys' not in st.session_state:
            st.session_state.user_denuncias_keys = []
        st.session_state.user_denuncias_keys.append(result['name'])
        
        st.success(f"✅ Comunicação enviada com sucesso! Protocolo: *{denuncia['protocolo']}*")
        st.info("Acompanhe o status na aba *Minhas Demandas*.")
        set_page('minhas_demandas')


def render_minhas_demandas_page():
    firebase = init_firebase()
    db = firebase.database()
    st.title("📋 Minhas Demandas")
    st.markdown("Acompanhe o status das comunicações que você enviou.")

    # Lógica para mostrar as demandas do usuário
    if 'user_denuncias_keys' not in st.session_state or not st.session_state.user_denuncias_keys:
        st.info("Você ainda não enviou nenhuma comunicação nesta sessão.")
        st.warning("⚠️ *Nota:* O histórico é mantido apenas enquanto você navega. Para um histórico permanente, seria necessário login.")
        return

    try:
        all_denuncias = db.child("denuncias").get().val()
        
        if all_denuncias:
            user_demandas = {k: v for k, v in all_denuncias.items() if k in st.session_state.user_denuncias_keys}

            if user_demandas:
                sorted_demandas = sorted(user_demandas.values(), key=lambda x: x['data'], reverse=True)
                
                for d in sorted_demandas:
                    status_color = "#f99417"
                    if "Resolvida" in d['status']:
                         status_color = "#2a9d8f"
                    elif "Em Execução" in d['status']:
                         status_color = "#1976d2"
                        
                    st.markdown(f"""
                        <div class="problem-card" style="border-left: 5px solid {status_color};">
                            <h4>{d['tipo']} - <span style="color: {status_color};">{d['status']}</span></h4>
                            <p style="font-size: 0.9rem;">Protocolo: <strong>{d['protocolo']}</strong></p>
                            <p>{d.get('descricao', 'Sem descrição.')[:70]}...</p>
                            <p>Data: {d['data'][:10]}</p>
                            {"<img src='" + d['foto_url'] + "' style='width: 100%; border-radius: 5px; margin-top: 10px;'>" if d.get('foto_url') else ""}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma demanda encontrada no seu histórico.")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar demandas: {str(e)}")


def render_mapa_ocorrencias_page():
    firebase = init_firebase()
    db = firebase.database()
    st.title("🗺️ Ocorrências na Região")
    st.markdown("Veja e confirme problemas relatados por outros cidadãos.")
    
    try:
        denuncias = db.child("denuncias").get().val()
        
        if denuncias:
            map_data = []
            confirmadas = {}
            for key, d in denuncias.items():
                try:
                    lat = float(d['lat'])
                    lng = float(d['lng'])
                    map_data.append({
                        'lat': lat,
                        'lon': lng,
                        'size': d.get("confirmacoes", 1) * 2 
                    })
                    if d.get("confirmacoes", 0) >= 2:
                        confirmadas[key] = d
                except ValueError:
                    continue 

            # Renderiza o Mapa 
            if map_data:
                st.map(map_data, zoom=12)
            else:
                 st.info("Aguardando coordenadas válidas para exibir o mapa.")

            st.subheader("Problemas Populares (≥2 Confirmações)")
            if confirmadas:
                for key, d in confirmadas.items():
                    st.markdown(f"""
                    <div class="problem-card">
                        <strong>{d['tipo']}</strong><br>
                        📍 Protocolo: {d['protocolo']}<br>
                        👥 {d['confirmacoes']} moradores confirmaram<br>
                        📅 Status: <span style="color: #f99417;">{d['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(key=f"form_{key}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            confirma_btn = st.form_submit_button("👍 Também vejo isso")
                        with col2:
                            resolve_btn = st.form_submit_button("✅ Resolvido (pela Prefeitura)")
                        
                        if confirma_btn:
                            nova_qtd = d.get("confirmacoes", 0) + 1
                            db.child("denuncias").child(key).update({"confirmacoes": nova_qtd})
                            st.success(f"Confirmação adicionada para {d['tipo']}!")
                            st.rerun()
                        
                        if resolve_btn:
                            db.child("denuncias").child(key).update({"status": "Resolvida - Cidadão Confirmou"})
                            st.success(f"Status de {d['tipo']} atualizado para RESOLVIDA!")
                            st.rerun()
            else:
                st.info("Nenhum problema com ≥2 confirmações ainda.")
        else:
            st.info("Nenhum problema registrado até agora.")
            
    except Exception as e:
        st.warning(f"⚠️ Sem conexão com o banco de dados. {str(e)}")


# =======================================================
# 🚀 4. LÓGICA DE NAVEGAÇÃO E BARRA INFERIOR
# =======================================================

# Renderiza a página atual baseada no 'session_state'
if st.session_state.page == 'home':
    render_home_page()
elif st.session_state.page == 'minhas_demandas':
    render_minhas_demandas_page()
elif st.session_state.page == 'mapa_ocorrencias':
    render_mapa_ocorrencias_page()
elif st.session_state.page == 'nova_comunicacao':
    render_denuncia_page()


# ----------------------------------------------------
# Barra de Navegação Inferior (Fixa)
# ----------------------------------------------------
# Nota: Esta barra usa JavaScript simples (onclick) para mudar o estado Streamlit (set_page)

# Inicia a barra
st.markdown("""
<div class="footer-nav">
""", unsafe_allow_html=True)

# 1. Ícone Home (icone_home.png)
st.markdown(f"""
    <button class="nav-button {'active' if st.session_state.page == 'home' else ''}" onclick="window.parent.document.querySelector('[data-testid="stSidebarContent"]').scroll(0,0); set_page('home')">
        <img src="icone_home.png" alt="Início">
        <span>Início</span>
    </button>
""", unsafe_allow_html=True)

# 2. Ícone Minhas Demandas (icone_demandas.png)
st.markdown(f"""
    <button class="nav-button {'active' if st.session_state.page == 'minhas_demandas' else ''}" onclick="window.parent.document.querySelector('[data-testid="stSidebarContent"]').scroll(0,0); set_page('minhas_demandas')">
        <img src="icone_demandas.png" alt="Demandas">
        <span>Demandas</span>
    </button>
""", unsafe_allow_html=True)

# 3. Botão Flutuante (Nova Comunicação) - ícone + ou icone_comunicar.png se preferir
st.markdown(f"""
    <div class="fab-container">
        <button class="fab-button {'active-fab' if st.session_state.page == 'nova_comunicacao' else ''}" onclick="window.parent.document.querySelector('[data-testid="stSidebarContent"]').scroll(0,0); set_page('nova_comunicacao')">
             + 
        </button>
    </div>
""", unsafe_allow_html=True)


# 4. Ícone Mapa (icone_mapa.png)
st.markdown(f"""
    <button class="nav-button {'active' if st.session_state.page == 'mapa_ocorrencias' else ''}" onclick="window.parent.document.querySelector('[data-testid="stSidebarContent"]').scroll(0,0); set_page('mapa_ocorrencias')">
        <img src="icone_mapa.png" alt="Mapa">
        <span>Mapa</span>
    </button>
""", unsafe_allow_html=True)

# 5. Ícone Mais/Serviços (icone_mais.png)
st.markdown(f"""
    <button class="nav-button" onclick="window.parent.document.querySelector('[data-testid="stSidebarContent"]').scroll(0,0); set_page('home')">
        <img src="icone_mais.png" alt="Mais">
        <span>Mais</span>
    </button>
""", unsafe_allow_html=True)

# Finaliza a barra
st.markdown("</div>", unsafe_allow_html=True)

# Rodapé simples (opcional, pode ser removido pois a barra de nav já está no rodapé)
st.markdown('<div class="footer">Comunica Guarulhos — Cidadania urbana com respeito.</div>', unsafe_allow_html=True)
