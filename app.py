import streamlit as st
import os
import requests
from pathlib import Path

def baixar_arquivo_google_drive(id_arquivo, destino):
    """
    Baixa um arquivo do Google Drive usando o ID do arquivo.
    """
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    
    # URL para download direto do Google Drive
    url = f"https://drive.google.com/uc?export=download&id={id_arquivo}"
    
    # Faz o download do arquivo
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()  # Verifica se houve erros na requisição
        
        # Mostra barra de progresso
        progress_text = "Baixando arquivo de dados..."
        progress_bar = st.progress(0, text=progress_text)
        
        # Calcula o tamanho total do arquivo
        total_size = int(r.headers.get('content-length', 0))
        bytes_downloaded = 0
        
        with open(destino, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    # Atualiza a barra de progresso
                    if total_size > 0:
                        progress = min(int((bytes_downloaded / total_size) * 100), 100)
                        progress_bar.progress(progress, text=f"{progress_text} {progress}%")
        
        progress_bar.empty()
        return True
    except Exception as e:
        st.error(f"Erro ao baixar o arquivo: {str(e)}")
        return False

# Configuração da página
st.set_page_config(page_title="Dashboard Salão", layout="wide")

# Redireciona para o dashboard do Salão
st.switch_page("pages/Dashboard_Salão_Atualizado.py")

if not os.path.exists(caminho_dados):
    with st.spinner('Preparando os dados...'):
        sucesso = baixar_arquivo_google_drive(id_arquivo_google_drive, caminho_dados)
        if not sucesso:
            st.error("Não foi possível baixar o arquivo de dados. Por favor, verifique sua conexão.")
            st.stop()

# Redireciona para a página do dashboard
st.switch_page("pages/Dashboard_FeeBased.py")
