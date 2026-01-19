import os
from pathlib import Path

import requests
import streamlit as st


def baixar_arquivo_google_drive(id_arquivo: str, destino: str) -> bool:
    """
    Baixa um arquivo do Google Drive usando o ID do arquivo (link de download direto).
    """
    destino_path = Path(destino)
    destino_path.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://drive.google.com/uc?export=download&id={id_arquivo}"

    try:
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()

        progress_text = "Baixando arquivo de dados..."
        progress_bar = st.progress(0, text=progress_text)

        total_size = int(r.headers.get("content-length", 0))
        bytes_downloaded = 0

        with open(destino_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                f.write(chunk)
                bytes_downloaded += len(chunk)

                if total_size > 0:
                    progress = min(int((bytes_downloaded / total_size) * 100), 100)
                    progress_bar.progress(progress, text=f"{progress_text} {progress}%")

        progress_bar.empty()
        return True

    except Exception as e:
        st.error(f"Erro ao baixar o arquivo: {e}")
        return False


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Dashboard Salão", layout="wide")

# =========================================================
# CONFIGURAÇÕES (AJUSTE AQUI)
# =========================================================
# 1) ID do arquivo no Google Drive (apenas o ID, não o link completo)
# Ex.: https://drive.google.com/file/d/SEU_ID/view  -> use SEU_ID
id_arquivo_google_drive = os.getenv("GDRIVE_FILE_ID", "").strip()

# 2) Caminho local onde o arquivo será salvo no deploy (Railway)
# Dica: use uma pasta dentro do projeto, ex.: data/arquivo.db (ou .xlsx/.csv)
caminho_dados = os.getenv("DATA_PATH", "data/dados.db").strip()

# =========================================================
# PREPARAÇÃO DOS DADOS (SE NECESSÁRIO)
# =========================================================
if not Path(caminho_dados).exists():
    if not id_arquivo_google_drive:
        st.error(
            "Arquivo de dados não encontrado e o ID do Google Drive não foi configurado.\n\n"
            "Defina a variável de ambiente **GDRIVE_FILE_ID** (ID do arquivo no Drive) "
            "ou envie o arquivo de dados junto no deploy."
        )
        st.stop()

    with st.spinner("Preparando os dados..."):
        sucesso = baixar_arquivo_google_drive(id_arquivo_google_drive, caminho_dados)
        if not sucesso:
            st.error("Não foi possível baixar o arquivo de dados. Verifique a conexão e o ID do Drive.")
            st.stop()

# =========================================================
# HOME (EVITA CRASH NO RAILWAY)
# =========================================================
st.title("Dashboard Salão")

st.markdown("Selecione abaixo qual dashboard você deseja abrir:")

col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/Dashboard_Salão_Atualizado.py",
        label="Abrir Dashboard Salão Atualizado",
        icon="📊",
    )

with col2:
    st.page_link(
        "pages/Dashboard_FeeBased.py",
        label="Abrir Dashboard FeeBased",
        icon="💼",
    )
