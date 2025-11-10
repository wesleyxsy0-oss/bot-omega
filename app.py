import streamlit as st
import pdfplumber
import io
import os
from datetime import datetime, timedelta
import pandas as pd

# Configuração da OpenAI (para análise de prescrição)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_OPENAI = True
except Exception as e:
    USE_OPENAI = False

# Estilo personalizado
st.set_page_config(page_title="Prescrição Fácil", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    h1 {
        color: #1a365d;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
    }
    .service-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    .analysis-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1a365d;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Menu lateral
st.sidebar.title("Prescrição Fácil")
st.sidebar.markdown("### Ferramentas Jurídicas Inteligentes")
servico = st.sidebar.selectbox("Escolha um serviço:", [
    "🔍 Análise de Prescrição (PDF)",
    "⏳ Cálculo de Prazos",
    "💰 Juros e Correção Monetária",
    "✅ Checklist de Defesas",
    "🛡️ Impenhorabilidade"
])

# =============================================
# SERVIÇO 1: ANÁLISE DE PRESCRIÇÃO (PDF + IA)
# =============================================
if servico == "🔍 Análise de Prescrição (PDF)":
    st.title("🔍 Análise de Prescrição")
    st.subheader("Envie um PDF de processo fiscal e receba análise de prescrição com IA")
    
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
                st.info(f"📄 PDF carregado. Analisando com IA...")
                if USE_OPENAI:
                    with st.spinner("🧠 Analisando com GPT-4..."):
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
                        st.markdown("### 📝 Análise da IA")
                        st.markdown(f'<div class="analysis-box">{response.choices[0].message.content}</div>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ IA não configurada.")
        except Exception as e:
            st.error(f"Erro: {str(e)}")

# =============================================
# SERVIÇO 2: CÁLCULO DE PRAZOS
# =============================================
elif servico == "⏳ Cálculo de Prazos":
    st.title("⏳ Cálculo de Prazos Processuais")
    st.subheader("Calcule prazos com contagem de dias úteis e feriados")
    
    data_inicial = st.date_input("Data inicial do prazo", value=datetime.today())
    dias_prazo = st.number_input("Número de dias (úteis)", min_value=1, value=15)
    uf = st.selectbox("Estado", ["SP", "RJ", "MG", "BA", "RS", "PR", "Outro"])
    
    if st.button("Calcular Prazo Final"):
        # Simples: adiciona dias corridos (para MVP)
        # Em versão avançada: usar workalendar
        data_final = data_inicial + timedelta(days=int(dias_prazo * 1.5))  # estimativa
        st.success(f"📅 Prazo final estimado: **{data_final.strftime('%d/%m/%Y')}**")
        st.info("ℹ️ Versão PRO inclui feriados estaduais e contagem exata de dias úteis.")

# =============================================
# SERVIÇO 3: JUROS E CORREÇÃO
# =============================================
elif servico == "💰 Juros e Correção Monetária":
    st.title("💰 Cálculo de Juros e Correção")
    st.subheader("Cálculo rápido para petições e condenações")
    
    valor = st.number_input("Valor inicial (R$)", min_value=0.0, value=1000.0)
    data_ini = st.date_input("Data inicial", value=datetime(2020, 1, 1))
    data_fim = st.date_input("Data final", value=datetime.today())
    indice = st.selectbox("Índice de correção", ["IPCA", "INPC", "SELIC", "Juros de 1% ao mês"])
    
    if st.button("Calcular"):
        dias = (data_fim - data_ini).days
        if indice == "Juros de 1% ao mês":
            meses = dias / 30
            valor_final = valor * (1 + 0.01) ** meses
        else:
            valor_final = valor * 1.35  # exemplo simplificado
        
        st.success(f"💰 Valor corrigido: **R$ {valor_final:,.2f}**")
        st.info("ℹ️ Versão PRO usa índices oficiais do IBGE e BACEN em tempo real.")

# =============================================
# SERVIÇO 4: CHECKLIST DE DEFESAS
# =============================================
elif servico == "✅ Checklist de Defesas":
    st.title("✅ Checklist de Defesas em Execução Fiscal")
    st.subheader("Responda rápido e receba defesas possíveis")
    
    tipo_cda = st.selectbox("Tipo de CDA", ["Tributária", "Não tributária"])
    citacao = st.radio("Foi citado?", ["Sim", "Não"])
    ultima_mov = st.number_input("Última movimentação (anos atrás)", 0, 10, 5)
    
    if st.button("Gerar Checklist"):
        defesas = []
        if ultima_mov >= 5:
            defesas.append("🟢 Prescrição intercorrente (5 anos sem movimentação)")
        if tipo_cda == "Tributária":
            defesas.append("📄 Verificar regularidade da CDA (art. 201 do CTN)")
        if citacao == "Não":
            defesas.append("❗ Nulidade por falta de citação válida")
        
        if defesas:
            st.markdown("### 📋 Defesas Sugeridas:")
            for d in defesas:
                st.write(d)
        else:
            st.info("Nenhuma defesa automática identificada. Consulte um advogado.")

# =============================================
# SERVIÇO 5: IMPENHORABILIDADE
# =============================================
elif servico == "🛡️ Impenhorabilidade":
    st.title("🛡️ Análise de Bens Impenhoráveis")
    st.subheader("Identifique bens que não podem ser penhorados")
    
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

# =============================================
# Rodapé
# =============================================
st.sidebar.markdown("---")
st.sidebar.info("Prescrição Fácil\nPlataforma jurídica inteligente para defesas fiscais")
