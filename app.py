import os
from pathlib import Path

import requests
import streamlit as st


# =========================================================
# FUNÇÃO: DOWNLOAD DO GOOGLE DRIVE
# =========================================================
def baixar_arquivo_google_drive(id_arquivo: str, destino: str) -> bool:
    """
    Baixa um arquivo do Google Drive usando o ID do arquivo.
    O arquivo precisa estar público ou compartilhado corretamente.
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
st.set_page_config(
    page_title="Dashboard Salão",
    layout="wide",
)

# =========================================================
# CONFIGURAÇÕES (VARIÁVEIS DE AMBIENTE)
# =========================================================
id_arquivo_google_drive = os.getenv("GDRIVE_FILE_ID", "").strip()
caminho_dados = os.getenv("DATA_PATH", "data/dados.db").strip()

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
# PREPARAÇÃO DOS DADOS
# =========================================================
if not Path(caminho_dados).exists():
    st.warning("Base de dados ainda não encontrada no servidor.")

    if not id_arquivo_google_drive:
        st.error(
            "Arquivo de dados não encontrado e o ID do Google Drive não foi configurado.\n\n"
            "Defina a variável de ambiente **GDRIVE_FILE_ID** no Railway."
        )
        st.stop()

    if st.button("Baixar dados agora"):
        with st.spinner("Preparando os dados..."):
            sucesso = baixar_arquivo_google_drive(
                id_arquivo_google_drive,
                caminho_dados,
            )

        if not sucesso:
            st.stop()

        st.success("Dados baixados com sucesso. Recarregue a página.")
        st.stop()

# =========================================================
# CONTEÚDO PRINCIPAL
# =========================================================
st.markdown("### Status")
st.success("Base de dados carregada com sucesso.")

st.markdown(
    """
    **Próximos passos:**
    - Acesse os dashboards pelo menu lateral  
    - Valide os dados carregados  
    - Ajuste visual/layout conforme necessidade
    """
)
