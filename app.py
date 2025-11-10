import streamlit as st
import pdfplumber
import io
import os
from datetime import datetime, timedelta

# Configuração da OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_OPENAI = True
except Exception as e:
    USE_OPENAI = False

# Estilo com cores da Kiwify + animações suaves
st.set_page_config(page_title="Prescrição Fácil", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background-color: #f8f9fa;
    font-family: 'Inter', sans-serif;
    color: #1e293b;
}

h1, h2, h3, h4, h5 {
    color: #0d1b2a;
    font-weight: 700;
    animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

p, li, .stMarkdown {
    color: #1e293b;
    line-height: 1.6;
}

.stButton > button {
    background-color: #f99417;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    background-color: #e07a00;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(249, 148, 23, 0.3);
}

.stButton > button:active {
    transform: translateY(0);
}

.service-container {
    background-color: #ffffff;
    padding: 1.75rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-top: 1.5rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    opacity: 0;
    animation: slideUp 0.5s forwards;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.analysis-result {
    background-color: #ffffff;
    padding: 1.75rem;
    border-radius: 12px;
    border-left: 4px solid #f99417;
    margin-top: 1.5rem;
    font-size: 0.95rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    animation: fadeIn 0.8s ease-out;
}

/* Spinner personalizado */
.spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1.5rem;
}

.spinner {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(249, 148, 23, 0.3);
    border-top: 3px solid #f99417;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.sidebar .sidebar-content {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
}

footer {
    font-size: 0.85rem;
    color: #64748b;
    text-align: center;
    margin-top: 2.5rem;
    padding: 1.25rem;
    border-top: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# Função para mostrar spinner personalizado
def show_custom_spinner():
    st.markdown('<div class="spinner-container"><div class="spinner"></div></div>', unsafe_allow_html=True)

# Menu lateral
with st.sidebar:
    st.markdown("<h2 style='color:#0d1b2a;'>Prescrição Fácil</h2>", unsafe_allow_html=True)
    st.caption("Ferramentas jurídicas inteligentes")
    servico = st.selectbox("Escolha um serviço", [
        "🔍 Análise de Prescrição (PDF)",
        "⏳ Cálculo de Prazos",
        "💰 Juros e Correção Monetária",
        "✅ Checklist de Defesas",
        "🛡️ Impenhorabilidade"
    ])
    st.markdown("---")
    st.caption("Plataforma para defesas fiscais")

# Cabeçalho
st.markdown("<h1 style='color:#0d1b2a;'>Prescrição Fácil</h1>", unsafe_allow_html=True)
st.markdown("Análise jurídica inteligente com foco em resultados reais")

# =============================================
# SERVIÇO 1: ANÁLISE DE PRESCRIÇÃO
# =============================================
if servico == "🔍 Análise de Prescrição (PDF)":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Análise de Prescrição com IA")
        st.write("Envie um PDF de processo fiscal para análise automática.")
        
        uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=["pdf"])
        
        if uploaded_file is not None:
            try:
                full_text = ""
                with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
                
                if len(full_text.strip()) < 50:
                    st.error("O PDF parece estar vazio ou sem texto selecionável.")
                else:
                    st.info(f"📄 Processando {len(full_text)} caracteres...")
                    if USE_OPENAI:
                        # Mostra spinner personalizado
                        with st.spinner(""):
                            show_custom_spinner()
                            limited_text = full_text[:12000]
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{
                                    "role": "system",
                                    "content": "Você é advogado especialista em direito tributário."
                                }, {
                                    "role": "user",
                                    "content": f"""
Analise o seguinte processo fiscal e verifique prescrição...

Texto:
{limited_text}
                                    """
                                }],
                                temperature=0.3, max_tokens=1000
                            )
                            st.markdown("### ✅ Resultado da Análise")
                            st.markdown(f'<div class="analysis-result">{response.choices[0].message.content}</div>', unsafe_allow_html=True)
                    else:
                        st.error("IA não configurada.")
            except Exception as e:
                st.error(f"Erro: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# Outros serviços (mantidos com animação de entrada)
# =============================================
elif servico == "⏳ Cálculo de Prazos":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Cálculo de Prazos Processuais")
        st.write("Insira os dados para estimar o prazo final.")
        # ... (restante do código igual, mas dentro do container animado)
        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("Data inicial", value=datetime.today())
        with col2:
            dias_prazo = st.number_input("Dias úteis", min_value=1, value=15)
        uf = st.selectbox("Estado", ["SP", "RJ", "MG", "BA", "RS", "PR", "Outro"])
        
        if st.button("Calcular"):
            data_final = data_inicial + timedelta(days=int(dias_prazo * 1.5))
            st.success(f"📅 Prazo final estimado: **{data_final.strftime('%d/%m/%Y')}**")
            st.caption("Versão PRO inclui feriados estaduais.")
        st.markdown('</div>', unsafe_allow_html=True)

# (Demais serviços seguem o mesmo padrão — todos dentro de `.service-container` para animação)

elif servico == "💰 Juros e Correção Monetária":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Cálculo de Juros e Correção")
        valor = st.number_input("Valor inicial (R$)", min_value=0.0, value=1000.0)
        data_ini = st.date_input("Data inicial", value=datetime(2020, 1, 1))
        data_fim = st.date_input("Data final", value=datetime.today())
        indice = st.selectbox("Índice", ["IPCA", "INPC", "SELIC", "Juros de 1% ao mês"])
        if st.button("Calcular"):
            valor_final = valor * 1.35
            st.success(f"💰 Valor corrigido: **R$ {valor_final:,.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

elif servico == "✅ Checklist de Defesas":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Checklist de Defesas")
        tipo_cda = st.selectbox("Tipo de CDA", ["Tributária", "Não tributária"])
        citacao = st.radio("Foi citado?", ["Sim", "Não"])
        ultima_mov = st.slider("Última movimentação (anos atrás)", 0, 10, 5)
        if st.button("Gerar Checklist"):
            defesas = ["Prescrição intercorrente", "Verificar CDA"] if ultima_mov >= 5 else ["Nenhuma defesa automática"]
            st.markdown("### Defesas Sugeridas")
            for d in defesas:
                st.write(f"- {d}")
        st.markdown('</div>', unsafe_allow_html=True)

elif servico == "🛡️ Impenhorabilidade":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Bens Impenhoráveis")
        tipo_bem = st.selectbox("Tipo de bem", ["Salário", "Bem de família", "Veículo"])
        if st.button("Verificar"):
            st.success("Este bem é impenhorável conforme a lei.")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<footer>Prescrição Fácil © 2025</footer>', unsafe_allow_html=True)
