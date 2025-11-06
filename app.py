import streamlit as st
import pandas as pd
import pdfplumber
from datetime import datetime
import io

st.set_page_config(page_title="Bot ÔMEGA", page_icon="⚖️", layout="wide")
st.title("⚖️ Bot ÔMEGA")
st.subheader("Análise Automática de Prescrição em CDAs e Execuções Fiscais")

st.markdown("""
📥 Faça upload de um **arquivo CSV** ou **PDF com tabela** contendo as colunas:
- `numero_cda`
- `data_fato_gerador` (AAAA-MM-DD)
- `data_inscricao` (AAAA-MM-DD)
- `data_citacao` (AAAA-MM-DD)
- `ultima_movimentacao` (AAAA-MM-DD)
- `valor` (opcional)

⚠️ **Dica**: PDF deve ter uma **tabela clara** (ex: relatório de sistema jurídico).
""")

# Modelo de CSV
example_csv = pd.DataFrame({
    "numero_cda": ["CDA-2015-00123"],
    "data_fato_gerador": ["2010-03-10"],
    "data_inscricao": ["2015-06-15"],
    "data_citacao": ["2016-01-20"],
    "ultima_movimentacao": ["2019-11-05"],
    "valor": [5000.00]
}).to_csv(index=False).encode('utf-8')

st.download_button("⬇️ Baixar modelo CSV", example_csv, "exemplo_cdas.csv", "text/csv")

# Upload
uploaded_file = st.file_uploader("Escolha seu arquivo (CSV ou PDF)", type=["csv", "pdf"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            # Extrair texto do PDF com pdfplumber
            tables = []
            with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        # Converte para DataFrame
                        df_page = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df_page)
            if not tables:
                st.error("❌ Nenhuma tabela encontrada no PDF.")
                st.stop()
            df = pd.concat(tables, ignore_index=True)
        else:
            st.error("Formato não suportado.")
            st.stop()

        # Verificar colunas obrigatórias
        required_cols = ["numero_cda", "data_fato_gerador", "data_inscricao", "data_citacao", "ultima_movimentacao"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ Faltam colunas! Esperadas: {required_cols}")
            st.stop()

        # Converter datas
        for col in required_cols[1:]:  # exceto numero_cda
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Analisar prescrição
        results = []
        for _, row in df.iterrows():
            # Prescrição inicial
            if pd.notna(row["data_fato_gerador"]) and pd.notna(row["data_inscricao"]):
                dias_fato_inscricao = (row["data_inscricao"] - row["data_fato_gerador"]).days
                presc_inicial = dias_fato_inscricao > 5 * 365
            else:
                presc_inicial = False

            # Prescrição intercorrente
            if pd.notna(row["data_citacao"]) and pd.notna(row["ultima_movimentacao"]):
                dias_sem_mov = (datetime.now() - row["ultima_movimentacao"]).days
                presc_inter = dias_sem_mov > 5 * 365
            else:
                presc_inter = False

            # Decisão
            if presc_inicial:
                status, risco, rec = "🟢 Prescrição Inicial", "Baixo", "Prescrição reconhecida – CDA nula"
            elif presc_inter:
                status, risco, rec = "🟡 Prescrição Intercorrente", "Médio", "Sugerir impugnação"
            else:
                status, risco, rec = "🔴 Sem prescrição aparente", "Alto", "Monitorar"

            results.append({
                "CDA": row["numero_cda"],
                "Status": status,
                "Risco": risco,
                "Recomendação": rec
            })

        result_df = pd.DataFrame(results)
        st.success("✅ Análise concluída!")
        st.dataframe(result_df.style.map(
            lambda x: "background-color: #d4edda" if "🟢" in str(x) else (
                "background-color: #fff3cd" if "🟡" in str(x) else "background-color: #f8d7da"
            ), subset=["Status"]
        ))

        st.download_button(
            "⬇️ Baixar resultado",
            result_df.to_csv(index=False).encode('utf-8'),
            "resultado_bot_omega.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"Erro ao processar: {str(e)}")
