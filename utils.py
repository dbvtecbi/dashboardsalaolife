import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def load_data(caminho_arquivo):
    """
    Carrega e pré-processa os dados do arquivo CSV.
    - Converte 'Data de Contratação' para datetime.
    - Garante que 'PL' e 'Taxa contratada' são numéricos.
    - Remove linhas onde 'Data de Contratação' é inválida.
    """
    try:
        # Lê o arquivo CSV com codificação UTF-8 e separador de vírgula
        df = pd.read_csv(
            caminho_arquivo,
            encoding='utf-8',
            sep=',',
            decimal='.',
            thousands=','
        )

        # Renomeia as colunas para o padrão esperado pelo app, garantindo a compatibilidade.
        df.rename(columns={
            'Data Contratação': 'Data de Contratação',
            'Taxa Contratação': 'Taxa contratada',
            'P/L': 'PL',
            'Código Cliente': 'Código do Cliente',
            'Nome Cliente': 'Nome do Cliente'
        }, inplace=True)

        # Pré-processamento dos dados
        if 'Status' in df.columns:
            df['Status'] = df['Status'].str.strip()  # Garante que não há espaços em branco

        # Converte a data para o formato datetime, tratando o formato brasileiro (DD/MM/YYYY)
        if 'Data de Contratação' in df.columns:
            # Primeiro tenta converter diretamente, depois tenta com o formato brasileiro
            df['Data de Contratação'] = pd.to_datetime(
                df['Data de Contratação'], 
                format='mixed',
                dayfirst=True,  # Para datas no formato DD/MM/YYYY
                errors='coerce'
            )

        # Garante que colunas numéricas são tratadas como tal e preenche NaNs com 0
        for col in ['PL', 'Taxa contratada']:
            if col in df.columns:
                # Remove caracteres não numéricos e converte para float
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(r'[^\d,.-]', '', regex=True)
                    df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado. Verifique se ele está na mesma pasta do aplicativo.")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar o arquivo: {e}")
        return pd.DataFrame()
