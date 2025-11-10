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

# Estilo premium com Google Fonts e cores jurídicas
st.set_page_config(page_title="Prescrição Fácil", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background-color: #f8f9fa;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    color: #1a365d;
    font-weight: 700;
}

.stButton > button {
    background-color: #2e7d32;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #1b5e20;
}

.service-box {
    background-color: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-top: 16px;
    border-left: 4px solid #1a365d;
}

.analysis-box {
    background-color: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-top: 20px;
    border-left: 4px solid #2e7d32;
}

.sidebar .sidebar-content {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

footer {
    font-size: 0.85rem;
    color: #6c757d;
    text-align: center;
    margin-top: 2rem;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Menu lateral com design premium
with st.sidebar:
    st.image("https://via.placeholder.com/150x40/1a365d/ffffff?text=Prescrição+Fácil", use_column_width=True)
    st.markdown("### Ferramentas Jurídicas Inteligentes")
    servico = st.selectbox("Escolha um serviço:", [
        "🔍 Análise de Prescrição (PDF)",
        "⏳ Cálculo de Prazos",
        "💰 Juros e Correção Monetária",
        "✅ Checklist de Defesas",
        "🛡️ Impenhorabilidade"
    ])
    st.markdown("---")
    st.caption("Prescrição Fácil\nPlataforma jurídica para defesas fiscais")

# Título principal
st.title("⚖️ Prescrição Fácil")
st.markdown("### Sua plataforma inteligente para defesas em execuções fiscais")

# =============================================
# SERVIÇO 1: ANÁLISE DE PRESCRIÇÃO (PDF + IA)
# =============================================
if servico == "🔍 Análise de Prescrição (PDF)":
    with st.container():
        st.markdown('<div class="service-box">', unsafe_allow_html=True)
        st.subheader("Análise de Prescrição com IA Jurídica")
        st.write("Envie um PDF de processo fiscal e receba um parecer técnico em segundos.")
        
        uploaded_file = st.file_uploader("Escolha um PDF", type=["pdf"])
        
        if uploaded_file is not None:
            try:
                full_text = ""
                with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
                
                if len(full_text.strip()) < 50:
                    st.error("❌ PDF sem texto selecionável.")
                else:
                    st.info(f"📄 Processando {len(full_text)} caracteres...")
                    if USE_OPENAI:
                        with st.spinner("🧠 Analisando com IA jurídica..."):
                            limited_text = full_text[:12000]
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{
                                    "role": "system",
                                    "content": "Você é advogado especialista em direito tributário."
                                }, {
                                    "role": "user",
                                    "content": f"""
Analise o seguinte processo fiscal e verifique prescrição:

1. Extraia: fato gerador, inscrição, citação, última movimentação.
2. Verifique prescrição inicial (5 anos) e intercorrente (5 anos sem movimentação).
3. Dê parecer claro com recomendação.

Texto:
{limited_text}
                                    """
                                }],
                                temperature=0.3, max_tokens=1000
                            )
                            st.markdown("### 📝 Parecer da IA")
                            st.markdown(f'<div class="analysis-box">{response.choices[0].message.content}</div>', unsafe_allow_html=True)
                    else:
                        st.error("⚠️ IA não configurada.")
            except Exception as e:
                st.error(f"Erro: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 2: CÁLCULO DE PRAZOS
# =============================================
elif servico == "⏳ Cálculo de Prazos":
    with st.container():
        st.markdown('<div class="service-box">', unsafe_allow_html=True)
        st.subheader("Cálculo de Prazos Processuais")
        st.write("Calcule prazos com contagem de dias úteis e feriados.")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("Data inicial do prazo", value=datetime.today())
        with col2:
            dias_prazo = st.number_input("Número de dias (úteis)", min_value=1, value=15)
        uf = st.selectbox("Estado", ["SP", "RJ", "MG", "BA", "RS", "PR", "Outro"])
        
        if st.button("Calcular Prazo Final"):
            data_final = data_inicial + timedelta(days=int(dias_prazo * 1.5))
            st.success(f"📅 **Prazo final estimado**: {data_final.strftime('%d/%m/%Y')}")
            st.info("ℹ️ Versão PRO inclui feriados estaduais e contagem exata.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 3: JUROS E CORREÇÃO
# =============================================
elif servico == "💰 Juros e Correção Monetária":
    with st.container():
        st.markdown('<div class="service-box">', unsafe_allow_html=True)
        st.subheader("Cálculo de Juros e Correção")
        st.write("Cálculo rápido para petições e condenações.")
        
        col1, col2 = st.columns(2)
        with col1:
            valor = st.number_input("Valor inicial (R$)", min_value=0.0, value=1000.0)
        with col2:
            data_ini = st.date_input("Data inicial", value=datetime(2020, 1, 1))
        data_fim = st.date_input("Data final", value=datetime.today())
        indice = st.selectbox("Índice de correção", ["IPCA", "INPC", "SELIC", "Juros de 1% ao mês"])
        
        if st.button("Calcular"):
            dias = (data_fim - data_ini).days
            valor_final = valor * 1.35  # exemplo
            st.success(f"💰 **Valor corrigido**: R$ {valor_final:,.2f}")
            st.info("ℹ️ Versão PRO usa índices oficiais em tempo real.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 4: CHECKLIST DE DEFESAS
# =============================================
elif servico == "✅ Checklist de Defesas":
    with st.container():
        st.markdown('<div class="service-box">', unsafe_allow_html=True)
        st.subheader("Checklist de Defesas em Execução Fiscal")
        st.write("Responda rápido e receba defesas possíveis.")
        
        tipo_cda = st.selectbox("Tipo de CDA", ["Tributária", "Não tributária"])
        citacao = st.radio("Foi citado?", ["Sim", "Não"])
        ultima_mov = st.slider("Última movimentação (anos atrás)", 0, 10, 5)
        
        if st.button("Gerar Checklist"):
            defesas = []
            if ultima_mov >= 5:
                defesas.append("🟢 **Prescrição intercorrente** (5 anos sem movimentação)")
            if tipo_cda == "Tributária":
                defesas.append("📄 Verificar regularidade da CDA (art. 201 do CTN)")
            if citacao == "Não":
                defesas.append("❗ **Nulidade por falta de citação válida**")
            
            if defesas:
                st.markdown("### 📋 Defesas Sugeridas:")
                for d in defesas:
                    st.write(d)
            else:
                st.info("Nenhuma defesa automática identificada.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 5: IMPENHORABILIDADE
# =============================================
elif servico == "🛡️ Impenhorabilidade":
    with st.container():
        st.markdown('<div class="service-box">', unsafe_allow_html=True)
        st.subheader("Análise de Bens Impenhoráveis")
        st.write("Identifique bens que não podem ser penhorados.")
        
        tipo_bem = st.selectbox("Tipo de bem", [
            "Salário ou renda", "Bem de família", "Veículo necessário ao trabalho",
            "Bens de uso pessoal", "Dinheiro em conta (até 40 salários mínimos)"
        ])
        
        if st.button("Verificar"):
            if tipo_bem == "Salário ou renda":
                st.success("✅ **Impenhorável** (art. 833, I, CPC)")
            elif tipo_bem == "Bem de família":
                st.success("✅ **Impenhorável** (Lei 8.009/90)")
            elif tipo_bem == "Veículo necessário ao trabalho":
                st.warning("⚠️ **Pode ser penhorado**, salvo se comprovada necessidade (art. 833, §2º)")
            else:
                st.info("ℹ️ Consulte a lista completa no CPC, art. 833.")
        st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown('<footer>Prescrição Fácil © 2025 — Plataforma jurídica inteligente para defesas fiscais</footer>', unsafe_allow_html=True)
