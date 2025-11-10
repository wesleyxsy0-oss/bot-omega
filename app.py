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

# Estilo com cores da Kiwify (profissional + destaque âmbar)
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
    transition: background-color 0.2s;
}

.stButton > button:hover {
    background-color: #e07a00;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(249, 148, 23, 0.3);
}

.service-container {
    background-color: #ffffff;
    padding: 1.75rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-top: 1.5rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.analysis-result {
    background-color: #ffffff;
    padding: 1.75rem;
    border-radius: 12px;
    border-left: 4px solid #f99417;
    margin-top: 1.5rem;
    font-size: 0.95rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.sidebar .sidebar-content {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
}

.sidebar .sidebar-content h1,
.sidebar .sidebar-content h2 {
    color: #0d1b2a;
}

.selectbox-label,
.radio-label {
    color: #0d1b2a !important;
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

# Menu lateral com cores da Kiwify
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

# Cabeçalho principal
st.markdown("<h1 style='color:#0d1b2a;'>Prescrição Fácil</h1>", unsafe_allow_html=True)
st.markdown("Análise jurídica inteligente com foco em resultados reais")

# =============================================
# SERVIÇO 1: ANÁLISE DE PRESCRIÇÃO (PDF + IA)
# =============================================
if servico == "🔍 Análise de Prescrição (PDF)":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Análise de Prescrição com IA")
        st.write("Envie um PDF de processo fiscal para análise automática de prescrição.")
        
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
                    st.info(f"Processando documento com {len(full_text)} caracteres...")
                    if USE_OPENAI:
                        with st.spinner("Analisando com inteligência artificial..."):
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
                            st.markdown("### Resultado da Análise")
                            st.markdown(f'<div class="analysis-result">{response.choices[0].message.content}</div>', unsafe_allow_html=True)
                    else:
                        st.error("IA não configurada. Verifique as credenciais.")
            except Exception as e:
                st.error(f"Erro ao processar: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 2: CÁLCULO DE PRAZOS
# =============================================
elif servico == "⏳ Cálculo de Prazos":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Cálculo de Prazos Processuais")
        st.write("Insira os dados para estimar o prazo final.")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("Data inicial", value=datetime.today())
        with col2:
            dias_prazo = st.number_input("Dias úteis", min_value=1, value=15)
        uf = st.selectbox("Estado", ["SP", "RJ", "MG", "BA", "RS", "PR", "Outro"])
        
        if st.button("Calcular"):
            data_final = data_inicial + timedelta(days=int(dias_prazo * 1.5))
            st.success(f"Prazo final estimado: **{data_final.strftime('%d/%m/%Y')}**")
            st.caption("Versão PRO inclui feriados estaduais e cálculo exato de dias úteis.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 3: JUROS E CORREÇÃO
# =============================================
elif servico == "💰 Juros e Correção Monetária":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Cálculo de Juros e Correção")
        st.write("Cálculo rápido para petições e condenações.")
        
        valor = st.number_input("Valor inicial (R$)", min_value=0.0, value=1000.0)
        data_ini = st.date_input("Data inicial", value=datetime(2020, 1, 1))
        data_fim = st.date_input("Data final", value=datetime.today())
        indice = st.selectbox("Índice", ["IPCA", "INPC", "SELIC", "Juros de 1% ao mês"])
        
        if st.button("Calcular"):
            valor_final = valor * 1.35  # simplificado
            st.success(f"Valor corrigido: **R$ {valor_final:,.2f}**")
            st.caption("Versão PRO usa índices oficiais em tempo real.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 4: CHECKLIST DE DEFESAS
# =============================================
elif servico == "✅ Checklist de Defesas":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Checklist de Defesas")
        st.write("Responda para receber sugestões de defesa.")
        
        tipo_cda = st.selectbox("Tipo de CDA", ["Tributária", "Não tributária"])
        citacao = st.radio("Foi citado?", ["Sim", "Não"])
        ultima_mov = st.slider("Última movimentação (anos atrás)", 0, 10, 5)
        
        if st.button("Gerar Checklist"):
            defesas = []
            if ultima_mov >= 5:
                defesas.append("Prescrição intercorrente (5 anos sem movimentação)")
            if tipo_cda == "Tributária":
                defesas.append("Verificar regularidade da CDA (art. 201 do CTN)")
            if citacao == "Não":
                defesas.append("Nulidade por falta de citação válida")
            
            if defesas:
                st.markdown("### Defesas Sugeridas")
                for d in defesas:
                    st.write(f"- {d}")
            else:
                st.info("Nenhuma defesa identificada.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SERVIÇO 5: IMPENHORABILIDADE
# =============================================
elif servico == "🛡️ Impenhorabilidade":
    with st.container():
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        st.subheader("Bens Impenhoráveis")
        st.write("Verifique se um bem pode ser penhorado.")
        
        tipo_bem = st.selectbox("Tipo de bem", [
            "Salário ou renda", "Bem de família", "Veículo necessário ao trabalho",
            "Bens de uso pessoal", "Dinheiro em conta (até 40 salários mínimos)"
        ])
        
        if st.button("Verificar"):
            if tipo_bem in ["Salário ou renda", "Bem de família"]:
                st.success("Este bem é impenhorável conforme a lei.")
            else:
                st.info("Pode ser penhorado, salvo exceções legais.")
        st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown('<footer>Prescrição Fácil © 2025 — Plataforma jurídica inteligente</footer>', unsafe_allow_html=True)
