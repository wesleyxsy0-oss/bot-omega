import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Bot ÔMEGA",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Bot ÔMEGA")
st.subheader("Análise Automática de Prescrição em CDAs e Execuções Fiscais")

st.markdown("""
📥 Faça upload de um arquivo CSV com as colunas abaixo:
- `numero_cda`
- `data_fato_gerador` (formato: AAAA-MM-DD)
- `data_inscricao` (formato: AAAA-MM-DD)
- `data_citacao` (formato: AAAA-MM-DD)
- `ultima_movimentacao` (formato: AAAA-MM-DD)
- `valor` (opcional)

⚠️ **Atenção**: datas devem estar no formato ISO (ex: 2015-06-15).
""")

# Botão para baixar exemplo
example_csv = pd.DataFrame({
    "numero_cda": ["CDA-2015-00123", "CDA-2013-00456", "CDA-2020-00789"],
    "data_fato_gerador": ["2010-03-10", "2008-07-22", "2019-11-05"],
    "data_inscricao": ["2015-06-15", "2013-09-30", "2020-12-10"],
    "data_citacao": ["2016-01-20", "2014-02-10", "2021-03-15"],
    "ultima_movimentacao": ["2019-11-05", "2014-02-10", "2021-03-15"],
    "valor": [5000.00, 12000.50, 3500.00]
}).to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Baixar modelo de CSV de exemplo",
    data=example_csv,
    file_name="exemplo_cdas.csv",
    mime="text/csv"
)

# Upload
uploaded_file = st.file_uploader("Escolha seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ["numero_cda", "data_fato_gerador", "data_inscricao", "data_citacao", "ultima_movimentacao"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Faltam colunas! Esperadas: {required_cols}")
        else:
            # Converter datas
            df["data_fato_gerador"] = pd.to_datetime(df["data_fato_gerador"])
            df["data_inscricao"] = pd.to_datetime(df["data_inscricao"])
            df["data_citacao"] = pd.to_datetime(df["data_citacao"])
            df["ultima_movimentacao"] = pd.to_datetime(df["ultima_movimentacao"])

            results = []
            for _, row in df.iterrows():
                # Prescrição inicial: 5 anos do fato à inscrição
                prescricao_inicial = (row["data_inscricao"] - row["data_fato_gerador"]).days > 5 * 365

                # Prescrição intercorrente: 5 anos sem movimentação após citação
                if pd.notna(row["data_citacao"]) and pd.notna(row["ultima_movimentacao"]):
                    dias_sem_mov = (datetime.now() - row["ultima_movimentacao"]).days
                    prescricao_intercorrente = dias_sem_mov > 5 * 365
                else:
                    prescricao_intercorrente = False

                # Decisão
                if prescricao_inicial:
                    status = "🟢 Prescrição Inicial"
                    risco = "Baixo"
                    rec = "Prescrição reconhecida – CDA nula"
                elif prescricao_intercorrente:
                    status = "🟡 Prescrição Intercorrente"
                    risco = "Médio"
                    rec = "Sugerir impugnação por prescrição intercorrente"
                else:
                    status = "🔴 Sem prescrição aparente"
                    risco = "Alto"
                    rec = "Monitorar ou avaliar outras defesas"

                results.append({
                    "CDA": row["numero_cda"],
                    "Status": status,
                    "Risco de Bloqueio": risco,
                    "Recomendação": rec,
                    "Data Fato": row["data_fato_gerador"].strftime("%d/%m/%Y") if pd.notna(row["data_fato_gerador"]) else "",
                    "Data Inscrição": row["data_inscricao"].strftime("%d/%m/%Y") if pd.notna(row["data_inscricao"]) else "",
                    "Última Mov.": row["ultima_movimentacao"].strftime("%d/%m/%Y") if pd.notna(row["ultima_movimentacao"]) else ""
                })

            result_df = pd.DataFrame(results)
            st.success("✅ Análise concluída!")
            st.dataframe(result_df.style.applymap(
                lambda x: "background-color: #d4edda" if "🟢" in str(x) else (
                    "background-color: #fff3cd" if "🟡" in str(x) else "background-color: #f8d7da"
                ), subset=["Status"]
            ))

            # Botão para download
            csv_output = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Baixar resultado",
                data=csv_output,
                file_name="resultado_bot_omega.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
