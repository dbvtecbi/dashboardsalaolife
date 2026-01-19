import os
from pathlib import Path

import requests
import streamlit as st


# =========================================================
# FUNÇÃO: DOWNLOAD DO GOOGLE DRIVE
# =========================================================
def baixar_arquivo_google_drive(id_arquivo: str, destino: str) -> bool:
    destino_path = Path(destino)
    destino_path.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://drive.google.com/uc?export=download&id={id_arquivo}"

    try:
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()

        total_size = int(r.headers.get("content-length", 0))
        bytes_downloaded = 0

        progress_bar = st.progress(0)

        with open(destino_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                f.write(chunk)
                bytes_downloaded += len(chunk)

                if total_size > 0:
                    progress = min(int((bytes_downloaded / total_size) * 100), 100)
                    progress_bar.progress(progress)

        progress_bar.empty()
        return True

    except Exception:
        return False


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Dashboard Salão",
    layout="wide",
)

# =========================================================
# VARIÁVEIS DE AMBIENTE
# =========================================================
id_arquivo_google_drive = os.getenv("GDRIVE_FILE_ID", "").strip()
caminho_dados = os.getenv("DATA_PATH", "data/dados.db").strip()

dados_existem = Path(caminho_dados).exists()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("DBV Capital")
    st.markdown("### Navegação")

    st.page_link(
        "pages/Dashboard_Salão_Atualizado.py",
        label="📊 Dashboard Salão Atualizado",
    )

    st.page_link(
        "pages/Dashboard_Salão_Life.py",
        label="💼 Dashboard Salão Life",
    )

# =========================================================
# HOME
# =========================================================
st.title("Dashboard Salão")
st.markdown(
    "Bem-vindo ao **Dashboard Salão**. Utilize o menu lateral para navegar "
    "entre os dashboards disponíveis."
)

# =========================================================
# PREPARAÇÃO SILENCIOSA DOS DADOS
# =========================================================
# ⚠️ Nenhuma mensagem de erro é exibida
# Se os dados não existirem, apenas não faz nada
if not dados_existem and id_arquivo_google_drive:
    with st.spinner("Carregando..."):
        baixar_arquivo_google_drive(
            id_arquivo_google_drive,
            caminho_dados,
        )

# =========================================================
# CONTEÚDO PRINCIPAL
# =========================================================
st.markdown("### Status do Sistema")

if dados_existem:
    st.success("Sistema pronto.")
else:
    # Mensagem neutra (opcional – pode remover se quiser tudo em branco)
    st.info("Sistema carregado.")
