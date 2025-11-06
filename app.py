import streamlit as st
import pandas as pd
import pdfplumber
import io
import os
from datetime import datetime

# Configuração da OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_OPENAI = True
except Exception as e:
    USE_OPENAI = False

st.set_page_config(page_title="Prescrição Fácil", page_icon="✅", layout="wide")
st.title("✅ Prescrição Fácil")
st.subheader("Analise processos fiscais completos com inteligência artificial")

st.markdown("""
📤 Envie um **PDF de processo jurídico** (ex: execução fiscal, certidão, sentença).  
A IA vai extrair as datas e verificar prescrição **automaticamente**.
""")

uploaded_file = st.file_uploader("Escolha um PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Extrair todo o texto do PDF
        full_text = ""
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        if len(full_text.strip()) < 50:
            st.error("❌ O PDF parece estar vazio ou sem texto selecionável.")
        else:
            st.info(f"📄 PDF carregado com {len(full_text)} caracteres. Enviando para análise com IA...")
            
            if USE_OPENAI:
                with st.spinner("🧠 Analisando com GPT-4..."):
                    # Limita o texto para evitar erro de tamanho
                    limited_text = full_text[:12000]
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Você é um advogado especialista em direito tributário e prescrição. Responda de forma clara, técnica e útil."},
                            {"role": "user", "content": f"""
Analise o seguinte trecho de um processo de execução fiscal e:

1. Extraia estas informações (se disponíveis):
   - Data do fato gerador
   - Data de inscrição na Dívida Ativa
   - Data da citação válida
   - Data da última movimentação útil

2. Verifique:
   - Prescrição inicial: 5 anos entre fato gerador e inscrição (CTN, art. 174)
   - Prescrição intercorrente: 5 anos sem movimentação após citação (CPC, art. 202)

3. Dê um parecer final claro com recomendação prática.

Texto do processo:
{limited_text}
                            """}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    
                    st.markdown("### 📝 **Análise da IA (GPT-4)**")
                    st.write(response.choices[0].message.content)
            else:
                st.error("⚠️ Erro: IA não configurada. Verifique a chave OPENAI_API_KEY no Render.")

    except Exception as e:
        st.error(f"Erro ao processar o PDF: {str(e)}")
