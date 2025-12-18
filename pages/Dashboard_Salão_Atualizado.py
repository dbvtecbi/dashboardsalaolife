# Dash_Salão_Atualizado.py

import re
import math
import sqlite3

# Controle de escala para ajuste de tamanho
TV_SCALE = 0.90  # ajuste fino: 0.80 a 0.96 (valores menores = elementos menores)
import unicodedata
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from textwrap import dedent

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# =====================================================
# CONFIGURAÇÃO DA PÁGINA (APENAS UMA VEZ)
# =====================================================
st.set_page_config(
    page_title="Dashboard DBV Capital",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# FUNÇÃO PARA DEBUG
# =====================================================
@st.cache_data(show_spinner=False)
def debug_data_loading() -> Dict[str, Any]:
    """
    Função para depuração do carregamento de dados.

    Returns:
        dict: Dicionário com informações de debug sobre arquivos e bancos de dados
    """
    debug_info: Dict[str, Any] = {
        "current_dir": str(Path(__file__).resolve().parent),
        "files_in_dir": [f.name for f in Path(__file__).parent.glob("*")],
        "db_files": [f.name for f in Path(__file__).parent.glob("*.db")],
    }

    # Verificar arquivos de banco de dados
    db_paths = {
        "positivador": Path(__file__).parent.parent / "DBV Capital_Positivador (MTD).db",
        "objetivos": Path(__file__).parent.parent / "DBV Capital_Objetivos.db",
    }

    for name, path in db_paths.items():
        debug_info[f"{name}_exists"] = path.exists()
        if path.exists():
            try:
                conn = sqlite3.connect(str(path))
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table';", conn
                )
                debug_info[f"{name}_tables"] = tables["name"].tolist()
                conn.close()
            except Exception as e:
                debug_info[f"{name}_error"] = str(e)

    return debug_info


# Mostrar informações de debug no sidebar
with st.sidebar.expander("🔍 Debug Info", expanded=False):
    try:
        debug_info = debug_data_loading()
        st.write("### Informações do Sistema")
        st.write(f"Diretório atual: `{debug_info['current_dir']}`")

        st.write("\n### Arquivos no diretório")
        st.write(f"Total de arquivos: {len(debug_info['files_in_dir'])}")
        st.write(
            "Arquivos de banco de dados encontrados:",
            "\n- " + "\n- ".join(debug_info.get("db_files", [])),
        )

        st.write("\n### Status dos Bancos de Dados")
        for db in ["positivador", "objetivos"]:
            exists = debug_info.get(f"{db}_exists", False)
            status = "✅ Encontrado" if exists else "❌ Não encontrado"
            st.write(f"- **{db.capitalize()}:** {status}")

            if exists and f"{db}_tables" in debug_info:
                st.write(f"  - Tabelas: {', '.join(debug_info[f'{db}_tables'])}")
            elif f"{db}_error" in debug_info:
                st.error(f"  - Erro: {debug_info[f'{db}_error']}")
    except Exception as e:
        st.error(f"Erro ao carregar informações de debug: {e}")
        st.text(traceback.format_exc())


def detectar_tabela_positivador(conn: sqlite3.Connection) -> str:
    """
    Detecta o nome correto da tabela no banco de dados.

    Ordem de prioridade:
    1. capital_positivador
    2. Relatório_Positivador (com acento)
    3. positivador
    4. positivador_mtd
    5. Primeira tabela disponível

    Args:
        conn: Conexão com o banco de dados SQLite

    Returns:
        str: Nome da tabela encontrada, entre aspas se contiver espaços
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tabelas = [row[0] for row in cursor.fetchall()]

        for tabela in [
            "capital_positivador",
            "Relatório_Positivador",
            "positivador",
            "positivador_mtd",
        ]:
            if tabela in tabelas:
                return f'"{tabela}"' if (" " in tabela or "-" in tabela) else tabela

        return f'"{tabelas[0]}"' if tabelas else ""
    except Exception as e:
        st.error(f"Erro ao detectar tabela: {e}")
        return ""


# =====================================================
# DEBUG - Funções para captação e transferências
# =====================================================
def _sum_captacao_positivador(df_in: pd.DataFrame, data_ini: datetime, data_fim: datetime) -> float:
    if df_in is None or df_in.empty:
        return 0.0
    if not {"Data_Posicao", "Captacao_Liquida_em_M"} <= set(df_in.columns):
        return 0.0

    aux = df_in[["Data_Posicao", "Captacao_Liquida_em_M"]].copy()
    aux["Data_Posicao"] = pd.to_datetime(aux["Data_Posicao"], errors="coerce")
    aux["Captacao_Liquida_em_M"] = pd.to_numeric(aux["Captacao_Liquida_em_M"], errors="coerce").fillna(0.0)

    m = (aux["Data_Posicao"] >= pd.Timestamp(data_ini)) & (aux["Data_Posicao"] <= pd.Timestamp(data_fim))
    return float(aux.loc[m, "Captacao_Liquida_em_M"].sum() or 0.0)


def _sum_transferencias(data_ini: datetime, data_fim: datetime) -> float:
    df_t = carregar_transferencias_intervalo_net(data_ini, data_fim)
    if df_t is None or df_t.empty or "pl_num_signed" not in df_t.columns:
        return 0.0
    return float(pd.to_numeric(df_t["pl_num_signed"], errors="coerce").fillna(0.0).sum() or 0.0)


def _garantir_data(df: pd.DataFrame, col_data: str) -> pd.DataFrame:
    """Garante que a coluna de data está no formato datetime e remove linhas inválidas."""
    df = df.copy()
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    return df.dropna(subset=[col_data])


def _periodo_mes_mais_recente(df: pd.DataFrame, col_data: str) -> tuple:
    """
    Encontra o período do mês mais recente nos dados.
    Retorna (inicio_mes, fim_mes, data_mais_recente)
    """
    dt_max = df[col_data].max()
    inicio_mes = dt_max.to_period("M").start_time
    fim_mes = (dt_max.to_period("M") + 1).start_time  # exclusive
    return inicio_mes, fim_mes, dt_max


def _sum_transferencias_por_mes_mais_recente() -> tuple[float, float]:
    """
    Calcula as transferências para o mês mais recente disponível.
    Retorna (transf_mes, transf_ano) onde:
    - transf_mes: soma do mês mais recente
    - transf_ano: soma do ano do mês mais recente
    """
    # Carrega todos os dados de transferências
    dbp = _find_transfer_db_path()
    if dbp is None:
        return 0.0, 0.0
    
    # Usa um intervalo amplo para pegar todos os dados disponíveis
    df = carregar_transferencias_intervalo_net(
        datetime(2000, 1, 1),  # Data inicial antiga
        datetime(2100, 1, 1)   # Data futura distante
    )
    
    if df is None or df.empty or "data_efetiva" not in df.columns:
        return 0.0, 0.0
    
    # Garante que temos a coluna de data
    df = _garantir_data(df, "data_efetiva")
    if df.empty:
        return 0.0, 0.0
    
    try:
        # Encontra o período do mês mais recente
        inicio_mes, fim_mes, dt_max = _periodo_mes_mais_recente(df, "data_efetiva")
        ano = dt_max.year
        
        # Calcula transferências do mês
        transf_mes = _sum_transferencias(inicio_mes, fim_mes)
        
        # Calcula transferências do ano
        inicio_ano = datetime(ano, 1, 1)
        transf_ano = _sum_transferencias(inicio_ano, datetime(ano + 1, 1, 1))
        
        return transf_mes, transf_ano
    except Exception as e:
        print(f"Erro ao calcular transferências: {e}")
        return 0.0, 0.0




# =====================================================
# CARREGAR POSITIVADOR (DBV Capital_Positivador.db) - compat
# =====================================================
@st.cache_data(show_spinner=False)
def carregar_dados_positivador(db_path_str: str, mtime: float) -> pd.DataFrame:
    """
    Carrega os dados do Positivador do banco de dados SQLite.
    Retorna um DataFrame com as colunas Data_Posicao e Net_Em_M.
    """
    try:
        db_path = Path(db_path_str)
        conn = sqlite3.connect(str(db_path))

        tabela = detectar_tabela_positivador(conn)
        if not tabela:
            st.error("Nenhuma tabela encontrada no banco de dados.")
            return pd.DataFrame()

        query = f"""
        SELECT
            [Data Posição] as Data_Posicao,
            [Net Em M] as Net_Em_M,
            [Captação Líquida em M] as Captacao_Liquida_em_M,
            [Assessor],
            [Cliente],
            [Status],
            [Data de Cadastro],
            [Data Atualização],
            [Tipo Pessoa],
            [Segmento],
            [Sexo],
            [Data de Nascimento],
            [Profissão],
            [Fez Segundo Aporte?],
            [Ativou em M?],
            [Evadiu em M?],
            [Operou Bolsa?],
            [Operou Fundo?],
            [Operou Renda Fixa?],
            [Aplicação Financeira Declarada Ajustada],
            [Receita no Mês],
            [Receita Bovespa],
            [Receita Futuros],
            [Receita RF Bancários],
            [Receita RF Privados],
            [Receita RF Públicos],
            [Captação Bruta em M],
            [Resgate em M],
            [Captação TED],
            [Captação ST],
            [Captação OTA],
            [Captação RF],
            [Captação TD],
            [Captação PREV],
            [Net em M 1],
            [Net Renda Fixa],
            [Net Fundos Imobiliários],
            [Net Renda Variável],
            [Net Fundos],
            [Net Financeiro],
            [Net Previdência],
            [Net Outros],
            [Receita Aluguel],
            [Receita Complemento Pacote Corretagem],
            [Data Posição] as Data_Posicao_Original,
            [Data Atualização] as Data_Atualizacao_Original
        FROM {tabela}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        df["Data_Posicao"] = pd.to_datetime(df["Data_Posicao"], errors="coerce")
        df["Net_Em_M"] = pd.to_numeric(df["Net_Em_M"], errors="coerce").fillna(0)
        df["Captacao_Liquida_em_M"] = pd.to_numeric(
            df["Captacao_Liquida_em_M"], errors="coerce"
        ).fillna(0)

        date_columns = ["Data de Cadastro", "Data de Nascimento", "Data Atualização"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        if "Assessor" in df.columns:
            df["assessor_code"] = (
                df["Assessor"].astype(str).str.extract(r"([A-Za-z0-9]+)")[0]
            )

        numeric_columns = [
            "Aplicação Financeira Declarada Ajustada",
            "Receita no Mês",
            "Receita Bovespa",
            "Receita Futuros",
            "Receita RF Bancários",
            "Receita RF Privados",
            "Receita RF Públicos",
            "Captação Bruta em M",
            "Resgate em M",
            "Captação TED",
            "Captação ST",
            "Captação OTA",
            "Captação RF",
            "Captação TD",
            "Captação PREV",
            "Net em M 1",
            "Net Renda Fixa",
            "Net Fundos Imobiliários",
            "Net Renda Variável",
            "Net Fundos",
            "Net Financeiro",
            "Net Previdência",
            "Net Outros",
            "Receita Aluguel",
            "Receita Complemento Pacote Corretagem",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Positivador: {e}")
        return pd.DataFrame()


# DataFrame usado pelos gráficos de AUC
_pos_path = Path(__file__).parent.parent / "DBV Capital_Positivador.db"
df_positivador = (
    carregar_dados_positivador(str(_pos_path), _pos_path.stat().st_mtime)
    if _pos_path.exists()
    else pd.DataFrame()
)

# =====================================================
# CONTROLE DE SEÇÕES
# =====================================================
EXIBIR_RENDA_VARIAVEL = False

# =====================================================
# CSS / LAYOUT (mantido)
# =====================================================
st.markdown(
    """
<style>

/* Remove todo espaço superior do Streamlit */
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Esconde sidebar completamente em modo TV */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Ajusta main para ocupar 100% sem sidebar */
section[data-testid="stMain"] {
    width: 100vw !important;
    margin-left: 0 !important;
}

/* Container principal sem margem - FULL WIDTH */
.block-container {
    padding: 0.3rem 0.5% !important;
    max-width: 100vw !important;
    width: 100vw !important;
    margin: 0 !important;
    background: transparent !important;
}

/* Remove margem que o Streamlit cria no topo do body */
html, body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100%;
    overflow-x: hidden;
}

/* Oculta completamente o menu e a barra superior do Streamlit */
header[data-testid="stHeader"] {
    display: none !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Styles (CSS) - mantido (apenas correção de indentação/estrutura)
# ---------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
    --tv-scale: 0.85;  /* REDUZIDO de 1.0 para 0.85 para melhor visualização em TV */
    --radius: calc(14px * var(--tv-scale));
    --border-width: 1px;
    --border-color: #d1d9d5;
    --border: var(--border-width) solid var(--border-color);
    --shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    --hover-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
    --bg-primary: #20352F;
    --bg-secondary: #1a2b26;
    --bg-odd: #1e2e29;
    --bg-even: #253a33;
    --text-primary: #ffffff;
    --text-secondary: #b8f7d4;
    --text-dark: #20352F;
    --accent: #2ecc71;
    --accent-hover: #27ae60;
    --transition: all 0.2s ease;
    --yellow: #948161;
    --tv-block-width: 100%;
    --page-bg: #20352F;
    --base-font-size: calc(0.9em * var(--tv-scale));
}

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow-x: hidden;
    background-color: var(--page-bg) !important;
    color: var(--text-dark) !important;
}

.stApp, [data-testid="stAppViewContainer"], .main {
    background: var(--page-bg) !important;
    color: var(--text-dark) !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}

[data-testid="stAppViewContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    background: var(--page-bg) !important;
}

.block-container {
    padding: 0.5rem 0.5% !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 auto !important;
    background: transparent !important;
}

.dashboard-card {
    background-color: var(--bg-primary) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;  /* Reduzido de 20px */
    box-shadow: var(--shadow) !important;
    color: var(--text-primary) !important;
    margin-bottom: 14px !important;  /* Reduzido de 20px */
    border: 1px solid #2ECC71 !important;
    transition: var(--transition) !important;
    font-size: 0.95em;  /* Fonte ligeiramente menor */
}

.dashboard-card:hover {
    box-shadow: var(--hover-shadow) !important;
}

.dashboard-card,
.dashboard-card h1,
.dashboard-card h2,
.dashboard-card h3,
.dashboard-card p,
.dashboard-card div,
.dashboard-card span {
    color: var(--text-primary) !important;
}

.metric-card-kpi {
    background: #20352F !important;
    border-radius: 12px !important;
    border: 1px solid #2ECC71 !important;
    padding: 4px 8px !important;
    margin: 2px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    color: white !important;
    height: auto !important;
    font-size: 0.9em;
}

[data-testid="stHorizontalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stHorizontalBlock"] {
    gap: 8px !important;
}

div[data-testid="stVerticalBlock"]:not(:has(.metric-card-kpi)) {
    background: transparent !important;
}

.section-title {
    color: var(--text-primary) !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
    padding-bottom: 4px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stPlotlyChart,
.table-container,
.plotly-graph-div {
    border-radius: var(--radius) !important;
    background: var(--bg-primary) !important;
    box-shadow: var(--shadow) !important;
    transition: var(--transition) !important;
    border: 1px solid #2ECC71 !important;
    padding: 8px 16px 4px 16px !important;
    overflow: visible !important;
    box-sizing: border-box;
    height: 100%;
    display: flex;
    flex-direction: column;
    margin: 0 !important;
}

.js-plotly-plot .plotly {
    background-color: transparent !important;
}

.modebar {
    background-color: transparent !important;
}

.modebar-btn svg {
    fill: var(--text-primary) !important;
}

.dashboard-card.nps-card {
    height: calc(300px * var(--tv-scale)) !important;
    min-height: calc(300px * var(--tv-scale)) !important;
    max-height: calc(300px * var(--tv-scale)) !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    margin-top: 0 !important;
    padding: 10px 12px !important;
}

.stPlotlyChart {
    height: calc(300px * var(--tv-scale)) !important;
    min-height: calc(300px * var(--tv-scale)) !important;
    max-height: calc(300px * var(--tv-scale)) !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    margin-top: 0 !important;
}

.stPlotlyChart > div {
    height: 100% !important;
}

.stPlotlyChart .js-plotly-plot,
.stPlotlyChart .plot-container {
    height: 100% !important;
}

.stPlotlyChart:hover,
.table-container:hover {
    box-shadow: var(--hover-shadow) !important;
    border-color: var(--accent) !important;
}

.col-tv-inner {
    max-width: 100%;
    width: 100%;
    margin: 0 !important;
    transform: none !important;
    transform-origin: top center !important;
}

.tv-metric-grid {
    height: calc(130px * var(--tv-scale)) !important;
    min-height: calc(130px * var(--tv-scale)) !important;
    margin-bottom: 0px !important;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: calc(5px * var(--tv-scale));
    overflow: hidden;
}

.metric-pill-top {
    padding: calc(2px * var(--tv-scale)) calc(2px * var(--tv-scale));
    min-height: calc(38px * var(--tv-scale));
}

.metric-pill-top .value {
    font-size: calc(0.85rem * var(--tv-scale));
}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;  /* Reduzido de 10px */
    margin: 8px 3px 14px 3px;  /* Reduzido */
    width: 100%;
}

.metric-pill {
    background-color: #334B43;
    border-radius: 10px;  /* Reduzido de 12px */
    padding: 5px 7px;  /* Reduzido de 6px 8px */
    border-left: 2px solid var(--accent) !important;  /* Mais fino */
    box-shadow: 0 2px 5px rgba(0,0,0,0.15);  /* Sombra mais suave */
    text-align: center;
    min-height: 62px;  /* Reduzido de 70px */
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
    font-size: 0.95em;  /* Fonte ligeiramente menor */
}

.metric-pill .label {
    font-weight: 600;
    color: #e9fff5;
    margin-bottom: 3px;  /* Reduzido de 4px */
    font-size: clamp(0.65rem, 0.82vw, 0.82rem);  /* Reduzido */
    line-height: 1.1;  /* Reduzido de 1.15 */
}

.metric-pill .value {
    font-weight: 800;
    color: #fff;
    font-size: clamp(0.82rem, 0.92vw, 0.96rem);  /* Reduzido */
    line-height: 1.1;  /* Reduzido de 1.15 */
}

.metric-pill-top {
    padding: 2px 4px;
    min-height: 44px;
    max-width: 260px;
    margin-left: auto;
    margin-right: auto;
    width: 100%;
}

.metric-pill-top .label {
    font-size: clamp(0.58rem, 0.65vw, 0.70rem);
}

.metric-pill-top .value {
    font-size: clamp(0.74rem, 0.80vw, 0.86rem);
}

.metric-pill-tv {
    background-color: #334B43;
    border-radius: 10px;
    padding: 4px 6px;
    border-left: 2px solid var(--accent) !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.12);
    text-align: center;
    min-height: 56px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.metric-pill-tv .label {
    font-weight: 600;
    color: #e9fff5;
    margin-bottom: 2px;
    font-size: clamp(0.60rem, 0.7vw, 0.7rem);
    line-height: 1.05;
}

.metric-pill-tv .value {
    font-weight: 800;
    color: #fff;
    font-size: clamp(0.78rem, 0.85vw, 0.88rem);
    line-height: 1.10;
}

.ranking-table {
  margin: 0 !important;
  width: 100%;
  border-collapse: collapse !important;
  border-spacing: 0 !important;
  font-size: 1.0em !important;
  color: var(--text-primary) !important;
  border-radius: 12px;
  overflow: hidden;
}

.ranking-table thead tr:first-child th {
  background: linear-gradient(135deg,
    rgba(46, 204, 113, 0.25),
    rgba(46, 204, 113, 0.12)
  ) !important;
  color: var(--accent) !important;
  font-weight: 700 !important;
  font-size: 1.1em !important;
  padding: 12px 10px !important;
  border: none !important;
  text-align: center !important;
  letter-spacing: 0.5px;
}

.ranking-table thead tr:nth-child(2) th {
  background: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
  border-bottom: 2px solid rgba(255,255,255,.1) !important;
  font-weight: 600 !important;
  padding: 10px 8px !important;
  text-align: center !important;
  font-size: 0.95em !important;
}

.ranking-table thead tr:nth-child(2) th + th {
  border-left: 1px solid rgba(255,255,255,.1) !important;
}

.ranking-table tbody td {
  padding: 10px 12px !important;
  text-align: center !important;
  border-bottom: 1px solid rgba(255,255,255,.08) !important;
  font-size: 1.05em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  height: 42px;
  box-sizing: border-box;
}

.ranking-table tbody tr:nth-child(odd) {
  background-color: var(--bg-odd);
}

.ranking-table tbody tr:nth-child(even) {
  background-color: var(--bg-even);
}

.ranking-table tbody tr:hover {
  background-color: var(--accent) !important;
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  transform: scale(1.01);
  transition: all 0.2s ease;
}

.nps-table-title {
  text-align: center;
  color: white;
  font-weight: 800;
  margin: 0 0 8px 0;
  font-size: 1.1em;
}

.objetivo-card-topo {
    background-color: #334B43;
    border-radius: 8px;  /* Reduzido de 10px */
    padding: 2px 6px;  /* Reduzido de 2px 8px */
    text-align: center;
    margin: 4px auto 8px auto;  /* Reduzido de 6px auto 10px auto */
    width: fit-content;
    border: 1px solid var(--accent);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);  /* Sombra mais suave */
    font-size: 0.95em;  /* Fonte ligeiramente menor */
}

.objetivo-card-topo span {
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.objetivo-card-topo .valor {
    color: var(--accent);
    margin-left: 6px;
    font-size: 0.90rem;
}

.dashboard-card-wrap {
    background-color: #212C28;
    border-radius: 12px;
    padding: 20px;
    border: var(--border) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
    position: relative;
}

.progress-wrapper {
    font-family: 'Segoe UI', Roboto, sans-serif;
    padding: 0;
    margin: calc(4px * var(--tv-scale)) 0 calc(18px * var(--tv-scale)) 0;
    max-width: 100%;
    width: 100%;
}

.progress-container {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
    width: 100%;
}

.progress-wrapper .progress-container:first-child {
    margin-bottom: 12px;
}

.progress-label {
    font-weight: 600;
    font-size: 0.8rem;
    color: #e9fff5;
    min-width: 60px;
    text-align: right;
    margin-right: 8px;
    letter-spacing: 0.3px;
}

.progress-bar-track {
    flex: 1;
    height: calc(40px * var(--tv-scale));
    background-color: #2a3f38;
    border-radius: calc(8px * var(--tv-scale));
    position: relative;
    overflow: hidden;
    box-shadow: inset 0 3px 6px rgba(0,0,0,0.3);
    border: 1px solid rgba(0,0,0,0.3);
    margin: calc(4px * var(--tv-scale)) 0;
    box-sizing: border-box;
}

.progress-bar-fill {
    position: absolute;
    top: 2px;
    bottom: 2px;
    left: 0;
    width: 0;
    background: linear-gradient(90deg, #2ecc71, #27ae60);
    border-radius: 7px;
    transition: width 0.5s ease-in-out;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.1);
}

.progress-bar-value-label {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-weight: 700;
    font-size: 0.75rem;
    padding: 1px 4px;
    white-space: nowrap;
    color: #ffffff;
    background-color: transparent;
    z-index: 2;
}

.progress-bar-limit-label {
    position: absolute;
    font-size: 0.75rem;
    color: #b8f7d4;
    top: 50%;
    transform: translateY(-50%);
    font-weight: 500;
    opacity: 0.9;
    z-index: 1;
}

.progress-bar-limit-label.left { left: 6px; text-align: left; }
.progress-bar-limit-label.right { right: 6px; text-align: right; }

.progress-bar-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(
        to right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.2) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    transform: translateX(-100%);
    animation: shine 2s infinite;
}

@keyframes shine {
    100% { transform: translateX(200%); }
}

@media (max-width: 1100px) {
  .metrics-row { grid-template-columns: repeat(2, 1fr); }
  .nps-grid, .rv-table-grid { grid-template-columns: 1fr; gap: 20px; }
}

.nps-card {
  margin-top: 0;
  margin-bottom: 0;
  padding: 14px 16px 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.nps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 10px;
    width: 100%;
    flex: 1;
}

.nps-grid .metric-pill { flex: 1; min-width: 0; }

.nps-card-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom: 12px;
}

.rv-card .nps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  width: 100%;
}

.rv-card .metric-pill {
    width: 100%;
    box-sizing: border-box;
    max-width: 100%;
    overflow: hidden;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    position: relative;
}

.rv-card .metric-row {
    display: grid;
    grid-template-columns: 1fr minmax(70px, auto) minmax(60px, auto);
    align-items: center;
    gap: 10px;
    padding: 5px 0;
    border-bottom: 1px solid #2ecc71;
}
.rv-card .metric-row:last-child { border-bottom: none; }

.rv-card .metric-label {
    min-width: 0;
    overflow: hidden;
    text-overflow: unset;
    white-space: normal;
    word-break: break-word;
    color: #fff;
    opacity: .9;
    font-size: .9rem;
    text-align: left;
}

.rv-card .metric-value {
    text-align: right;
    font-weight: 700;
    color: #fff;
    font-size: .98rem;
    white-space: nowrap;
    min-width: 0;
}

.rv-table-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.col-tv-inner .progress-bar-track { height: calc(70px * var(--tv-scale)); }
.col-tv-inner .progress-bar-fill { top: 6px; bottom: 6px; }
.col-tv-inner .progress-bar-value-label { font-size: calc(0.90rem * var(--tv-scale)); }
.col-tv-inner .progress-label { font-size: calc(0.85rem * var(--tv-scale)); }

.tv-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: calc(12px * var(--tv-scale));
  row-gap: calc(10px * var(--tv-scale));
  max-width: 100%;
  width: 100%;
  margin: calc(10px * var(--tv-scale)) 0 0 0;
}

.tv-metric-grid .metric-pill.metric-pill-top {
  max-width: 100%;
  width: 100%;
  margin-left: 0;
  margin-right: 0;
}

.col-tv-inner .top3-h-wrap {
  max-width: 100%;
  margin-left: 0;
  margin-right: 0;
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
div[data-testid="stVerticalBlock"]:has(.metric-card-kpi) {
    background: #20352F !important;
    border-radius: 20px !important;
    border: 1px solid #2ECC71 !important;
    padding: 10px 16px 8px 16px !important;
    margin: 4px 4px 8px 4px !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.45);
}

.col-tv-inner .top3-h-wrap {
    margin-top: 10px !important;
    margin-bottom: 0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# Constantes & Mapeamento
# =====================================================
YELLOW = "#948161"
GREEN = "#2ecc71"

ASSESSORES_MAP = {
    "A92300": "Adil Amorim",
    "A95715": "André Norat",
    "A87867": "Arthur Linhares",
    "A95796": "Artur Vaz",
    "A95642": "Bruna Lewis",
    "A26892": "Carlos Monteiro",
    "A71490": "Cesar Lima",
    "A93081": "Daniel Morone",
    "A23594": "Diego Monteiro",
    "A23454": "Eduardo Monteiro",
    "A91619": "Eduardo Parente",
    "A95635": "Enzo Rei",
    "A50825": "Fabiane Souza",
    "A46886": "Fábio Tomaz",
    "A96625": "Gustavo Levy",
    "A95717": "Henrique Vieira",
    "A94115": "Israel Oliveira Moraes",
    "A97328": "João Goldenberg ",
    "A41471": "João Pedro Georg de Andrade",
    "A69453": "Guilherme Peçanha",
    "A51586": "Luiz Eduardo Mesquita",
    "A28215": "Luiz Coimbra",
    "A92301": "Marcus Faria",
    "A38061": "Paulo Pinho",
    "A69265": "Paulo Gomes",
    "A25214": "Renato Zanin",
    "A21652": "Rodrigo Teísta",
    "A93282": "Samuel Monteiro",
    "A72213": "Thiago Cordeiro",
    "A26914": "Victor Garrido",
}
NOME_TO_COD = {v.upper(): k for k, v in ASSESSORES_MAP.items()}


def obter_nome_assessor(codigo: str) -> str:
    if not codigo:
        return "-"
    codigo_str = str(codigo).strip()
    # Tenta com o código original
    if codigo_str in ASSESSORES_MAP:
        return ASSESSORES_MAP[codigo_str]
    # Tenta adicionar prefixo A se for numérico
    if codigo_str.isdigit():
        codigo_com_a = f"A{codigo_str}"
        if codigo_com_a in ASSESSORES_MAP:
            return ASSESSORES_MAP[codigo_com_a]
    # Tenta remover prefixo A se existir
    if codigo_str.startswith("A") and codigo_str[1:].isdigit():
        if codigo_str in ASSESSORES_MAP:
            return ASSESSORES_MAP[codigo_str]
    return codigo_str


# =====================================================
# Helpers de Formatação / Datas
# =====================================================
def formatar_valor_curto(valor: Any) -> str:
    try:
        v = float(valor or 0)
    except (ValueError, TypeError):
        return "R$ 0"

    if v >= 1_000_000_000:
        return f"R$ {v / 1_000_000_000:.1f}bi"
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v / 1_000:.1f}K"
    return f"R$ {v:,.0f}"


def fmt_valor_simples(v: Any) -> str:
    try:
        v = float(v)
    except Exception:
        return str(v)

    if v < 0:
        return f"-{fmt_valor_simples(abs(v))}"
    if v >= 1_000_000:
        return f"R$ {int(round(v / 1_000_000))}M"
    if v >= 1_000:
        return f"R$ {int(round(v / 1_000))}K"
    return f"R$ {int(round(v))}"


def fmt_valor(v: Any) -> str:
    try:
        v = float(v)
    except Exception:
        return str(v)

    if v < 0:
        return f"-{fmt_valor(abs(v))}"
    if v >= 1_000_000:
        return fmt_valor_simples(v)
    if v >= 1_000:
        return f"R$ {v / 1_000:,.0f}K".replace(",", "X").replace(".", ",").replace("X", ".")
    if v == int(v):
        return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")


def arredondar_valor(valor: Any, casas_decimais: int = 2) -> float:
    try:
        if valor is None:
            return 0.0
        fator = 10**casas_decimais
        return float(int(valor * fator + 0.5) / fator)
    except (TypeError, ValueError):
        return 0.0


def fmt_pct(x: Any) -> str:
    try:
        x = arredondar_valor(float(x) * 100, 2)
        return f"{x:,.2f}%".replace(".", "X").replace(",", ".").replace("X", ",")
    except Exception:
        return "-"


def _mes_pt(m: int) -> str:
    """Retorna o nome do mês em português"""
    meses = [
        "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
        "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
    ]
    return meses[m-1] if 1 <= int(m) <= 12 else "-"


def filtrar_nps_a_partir_de_junho(df_nps: pd.DataFrame) -> tuple:
    """
    Mantém somente respostas cuja data_resposta esteja no ciclo:
    01/06 (ano base) até 31/05 (ano seguinte).
    O ano base é definido pela última data_resposta existente no df.
    """
    if df_nps is None or df_nps.empty or "data_resposta" not in df_nps.columns:
        return df_nps, "-"

    aux = df_nps.copy()
    aux["data_resposta"] = pd.to_datetime(aux["data_resposta"], errors="coerce", dayfirst=True)
    aux = aux.dropna(subset=["data_resposta"])
    if aux.empty:
        return aux, "-"

    dt_max = pd.Timestamp(aux["data_resposta"].max()).normalize()

    # ciclo começa em junho
    inicio = pd.Timestamp(dt_max.year, 6, 1)
    if dt_max.month < 6:
        inicio = pd.Timestamp(dt_max.year - 1, 6, 1)

    fim_excl = inicio + pd.DateOffset(years=1)  # exclusivo (01/06 do ano seguinte)
    aux = aux[(aux["data_resposta"] >= inicio) & (aux["data_resposta"] < fim_excl)].copy()

    # Ajustando o label para mostrar o mês de junho no final também
    fim_incl = fim_excl - pd.Timedelta(days=1)
    # Se o mês final for maio, mostramos junho
    if fim_incl.month == 5:
        label = f"{_mes_pt(inicio.month)} {inicio.year} - {_mes_pt(fim_incl.month + 1)} {fim_incl.year}"
    else:
        label = f"{_mes_pt(inicio.month)} {inicio.year} - {_mes_pt(fim_incl.month)} {fim_incl.year}"
    return aux, label


def _pct_br(v: float) -> str:
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def _media_br(v: float) -> str:
    try:
        return f"{float(v):.2f}".replace(".", ",")
    except Exception:
        return "0,00"


def ultima_data(
    df: pd.DataFrame, date_col: str = "Data_Posicao", filter_col: Optional[str] = None
) -> Optional[datetime]:
    if date_col not in df.columns:
        return None
    s = df[date_col]
    if filter_col and filter_col in df.columns:
        s = df.loc[df[filter_col].notna(), date_col]
    s = pd.to_datetime(s, errors="coerce").dropna()
    if s.empty:
        return None
    return s.max()


def extract_assessor_code(x: Any) -> Optional[str]:
    s = str(x or "").strip()
    if not s:
        return None
    up = re.sub(r"\s+", " ", s).upper()

    m = re.search(r"A\s*?(\d{5})", up)
    if m:
        return f"A{m.group(1)}"

    m2 = re.search(r"(^|\D)(\d{5})(\D|$)", up)
    if m2:
        return f"A{m2.group(2)}"

    if up in NOME_TO_COD:
        return NOME_TO_COD[up]

    return None


def _primeiro_nome_sobrenome(nome_completo: str) -> str:
    if not nome_completo:
        return "-"
    tokens = re.split(r"\s+", str(nome_completo).strip())
    if not tokens:
        return "-"
    if len(tokens) == 1:
        return tokens[0]

    particulas = {"de", "da", "das", "do", "dos", "e"}
    nome = tokens[0]
    sobrenome = None
    for t in tokens[1:]:
        if t.lower() in particulas:
            continue
        sobrenome = t
        break
    if not sobrenome:
        sobrenome = tokens[1]
    return f"{nome} {sobrenome}"


def _strip_accents(txt: str) -> str:
    if txt is None:
        return ""
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", str(txt)) if not unicodedata.combining(ch)
    )


def _norm_upper_noaccents_series(s: pd.Series) -> pd.Series:
    return s.astype(str).map(_strip_accents).str.upper().str.strip().fillna("")


# =====================================================
# Transferências
# =====================================================
def _find_transfer_db_path() -> Optional[Path]:
    base_dir = Path(__file__).parent.parent
    candidates = [
        base_dir / "DBV Capital_Transferências.db",
        base_dir / "DBV Capital_Transferencias.db",
        Path("DBV Capital_Transferências.db"),
        Path("DBV Capital_Transferencias.db"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _norm_colname(c: str) -> str:
    s = _strip_accents(str(c)).lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _pick_transfers_table(conn: sqlite3.Connection) -> Optional[str]:
    try:
        tabs = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            conn,
        )["name"].tolist()
        if not tabs:
            return None

        preferred = {"transferencias", "transferências", "transferencia", "transferência"}
        for t in tabs:
            if _norm_colname(t) in preferred:
                return t

        best_t, best_score = None, -1
        for t in tabs:
            try:
                cols = pd.read_sql_query(f'PRAGMA table_info("{t}");', conn)["name"].tolist()
            except Exception:
                continue
            ncols = {_norm_colname(c) for c in cols}
            score = 0
            score += int("pl" in ncols)
            score += int("data solicitacao" in ncols)
            score += int("data transferencia" in ncols)
            score += int("codigo assessor destino" in ncols or "cod assessor destino" in ncols)
            if score > best_score:
                best_score = score
                best_t = t

        return best_t or tabs[0]
    except Exception:
        return None


def _parse_money_like_series(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)

    def conv(x: str):
        if x in ("", "nan", "NaN", "None", "NULL"):
            return np.nan
        if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", x):
            return float(x.replace(".", "").replace(",", "."))
        if re.match(r"^\d{1,3}(,\d{3})+(\.\d+)?$", x):
            return float(x.replace(",", ""))
        if "," in x and "." not in x:
            return float(x.replace(",", "."))
        return float(x)

    out = s.map(lambda v: conv(v) if v is not None else np.nan)
    return pd.to_numeric(out, errors="coerce").fillna(0.0)


@st.cache_data(show_spinner=False)
def _carregar_dados_transferencias_cached(db_path_str: str, mtime: float) -> pd.DataFrame:
    try:
        with sqlite3.connect(db_path_str) as conn:
            table = _pick_transfers_table(conn)
            if not table:
                return pd.DataFrame()
            df = pd.read_sql_query(f'SELECT * FROM "{table}";', conn)
        return df
    except Exception:
        return pd.DataFrame()


def carregar_dados_transferencias() -> pd.DataFrame:
    dbp = _find_transfer_db_path()
    if dbp is None:
        return pd.DataFrame()
    return _carregar_dados_transferencias_cached(str(dbp), dbp.stat().st_mtime)


def tratar_dados_transferencias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza Transferências:
    - data_efetiva = Data Solicitação (preferencial) senão Data Transferencia
    - pl_num = PL (numérico)
    - assessor_code = Código Assessor Destino (extraído)
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["data_efetiva", "pl_num", "assessor_code"])

    cols_norm = {_norm_colname(c): c for c in df.columns}

    c_solic = cols_norm.get("data solicitacao")
    c_transf = cols_norm.get("data transferencia")
    c_pl = cols_norm.get("pl")
    c_ass = (
        cols_norm.get("codigo assessor destino")
        or cols_norm.get("cod assessor destino")
        or cols_norm.get("assessor destino")
    )

    out = df.copy()

    s_solic = out[c_solic] if c_solic in out.columns else pd.Series([pd.NA] * len(out))
    s_trans = out[c_transf] if c_transf in out.columns else pd.Series([pd.NA] * len(out))

    d1 = pd.to_datetime(s_solic, errors="coerce", dayfirst=True, infer_datetime_format=True)
    d2 = pd.to_datetime(s_trans, errors="coerce", dayfirst=True, infer_datetime_format=True)

    out["data_efetiva"] = d1
    out.loc[out["data_efetiva"].isna(), "data_efetiva"] = d2[out["data_efetiva"].isna()]

    if c_pl in out.columns:
        out["pl_num"] = _parse_money_like_series(out[c_pl])
    else:
        out["pl_num"] = 0.0

    if c_ass in out.columns:
        out["assessor_code"] = out[c_ass].map(extract_assessor_code)
    else:
        out["assessor_code"] = pd.NA

    out = out.dropna(subset=["data_efetiva", "assessor_code"])
    out = out[out["pl_num"] != 0]

    return out[["data_efetiva", "pl_num", "assessor_code"]].copy()


def obter_periodos_referencia(df_positivador_in: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Define períodos MTD e YTD usando a ÚLTIMA Data_Posicao existente no Positivador.
    - MTD: do 1º dia do mês da última data até a própria última data
    - YTD: de 01/01 do ano da última data até a própria última data
    """
    if df_positivador_in.empty or "Data_Posicao" not in df_positivador_in.columns:
        return None

    data_fim = pd.to_datetime(df_positivador_in["Data_Posicao"]).max()
    data_fim = data_fim.normalize()

    mtd_ini = data_fim.replace(day=1)
    ytd_ini = datetime(data_fim.year, 1, 1)

    return {
        "data_fim": data_fim,
        "mtd_ini": mtd_ini,
        "ytd_ini": ytd_ini,
        "ano_ref": data_fim.year,
        "mes_ref": data_fim.strftime("%Y-%m"),
    }


def obter_periodos_referencia_por_ano(df_positivador_in: pd.DataFrame, ano_alvo: int) -> Optional[Dict[str, Any]]:
    """
    Períodos MTD/YTD ancorados em um ANO específico.
    - data_fim = última Data_Posicao disponível dentro do ano_alvo
    - MTD = 1º dia do mês de data_fim até data_fim
    - YTD = 01/01/ano_alvo até data_fim
    """
    if df_positivador_in is None or df_positivador_in.empty or "Data_Posicao" not in df_positivador_in.columns:
        return None

    s = pd.to_datetime(df_positivador_in["Data_Posicao"], errors="coerce").dropna()
    s_ano = s[s.dt.year == int(ano_alvo)]
    if s_ano.empty:
        return None

    data_fim = s_ano.max().normalize()
    mtd_ini = data_fim.replace(day=1)
    ytd_ini = datetime(int(ano_alvo), 1, 1)

    return {
        "data_fim": data_fim,
        "mtd_ini": mtd_ini,
        "ytd_ini": ytd_ini,
        "ano_ref": int(ano_alvo),
        "mes_ref": data_fim.strftime("%Y-%m"),
    }


def _qident(name: str) -> str:
    """Quote seguro para identificadores SQLite (colunas/tabelas)."""
    return f'"{str(name).replace(chr(34), chr(34)*2)}"'


def _sql_date_conv_expr(col_sql: str) -> str:
    """
    Converte 'DD/MM/YYYY ...' -> 'YYYY-MM-DD' ou mantém ISO 'YYYY-MM-DD ...'
    Retorna string YYYY-MM-DD (ou NULL).
    """
    return f"""
    CASE
        WHEN {col_sql} IS NULL OR TRIM(CAST({col_sql} AS TEXT)) = '' THEN NULL
        WHEN INSTR(CAST({col_sql} AS TEXT), '/') > 0 THEN
            SUBSTR(CAST({col_sql} AS TEXT), 7, 4) || '-' ||
            SUBSTR(CAST({col_sql} AS TEXT), 4, 2) || '-' ||
            SUBSTR(CAST({col_sql} AS TEXT), 1, 2)
        ELSE
            SUBSTR(CAST({col_sql} AS TEXT), 1, 10)
    END
    """.strip()


def _pick_transfer_cols(df_cols: List[str]) -> Dict[str, Optional[str]]:
    """
    Mapeia nomes prováveis das colunas do seu DB de Transferências para um padrão.
    """
    cols_norm = {_norm_colname(c): c for c in df_cols}

    def get(*keys: str) -> Optional[str]:
        for k in keys:
            if k in cols_norm:
                return cols_norm[k]
        return None

    return {
        "cliente": get("cliente"),
        "pl": get("pl"),
        "data_solic": get("data solicitacao", "data solicit", "data solicitacao transferencia"),
        "data_transf": get("data transferencia", "data transf"),
        "tipo": get("tipo"),
        "status": get("status"),
        "cod_origem": get("codigo assessor origem", "cod assessor origem", "assessor origem"),
        "nome_origem": get("nome assessor origem", "assessor origem nome", "nome origem"),
        "cod_destino": get("codigo assessor destino", "cod assessor destino", "assessor destino"),
        "nome_destino": get("nome assessor destino", "assessor destino nome", "nome destino"),
    }


@st.cache_data(show_spinner=False)
def _carregar_transferencias_intervalo_sql_cached(
    db_path_str: str,
    mtime: float,
    data_ini_iso: str,
    data_fim_iso: str,
) -> pd.DataFrame:
    """
    Carrega transferências já filtradas no SQLite:
    - cliente = 'Externo' (case-insensitive)
    - status = 'Concluído' (quando existir coluna)
    - pl válido
    - data efetiva = COALESCE(data_solicitacao_conv, data_transferencia_conv) entre data_ini e data_fim
      (MESMA prioridade do Dash Captação)
    """
    dbp = Path(db_path_str)
    if not dbp.exists():
        return pd.DataFrame()

    try:
        with sqlite3.connect(str(dbp)) as conn:
            table = _pick_transfers_table(conn)
            if not table:
                return pd.DataFrame()

            cols = pd.read_sql_query(f"PRAGMA table_info({_qident(table)});", conn)["name"].tolist()
            mp = _pick_transfer_cols(cols)

            c_cliente = mp["cliente"]
            c_pl = mp["pl"]
            c_solic = mp["data_solic"]
            c_transf = mp["data_transf"]
            c_status = mp["status"]  # <- agora vamos usar

            # sem essas, não dá pra aplicar corretamente
            if not c_cliente or not c_pl or (not c_solic and not c_transf):
                return pd.DataFrame()

            # opcionais
            c_tipo = mp["tipo"]
            c_cod_o = mp["cod_origem"]
            c_nome_o = mp["nome_origem"]
            c_cod_d = mp["cod_destino"]
            c_nome_d = mp["nome_destino"]

            t = _qident(table)

            def col_or_null(c: Optional[str], alias: str) -> str:
                return f"{_qident(c)} AS {alias}" if c else f"NULL AS {alias}"

            c_cliente_sql = _qident(c_cliente)
            c_pl_sql = _qident(c_pl)
            c_solic_sql = _qident(c_solic) if c_solic else "NULL"
            c_transf_sql = _qident(c_transf) if c_transf else "NULL"

            solic_conv = _sql_date_conv_expr(c_solic_sql) if c_solic else "NULL"
            transf_conv = _sql_date_conv_expr(c_transf_sql) if c_transf else "NULL"

            # ---- filtro de status (igual ao Captação)
            # aceita "Concluído" e "Concluido" (com/sem acento), em qualquer caixa
            status_where = ""
            if c_status:
                status_sql = f"LOWER(TRIM(CAST({_qident(c_status)} AS TEXT)))"
                status_where = f"AND {status_sql} IN ('concluido', 'concluído')"

            # ---- prioridade de data (igual ao Captação): solicitacao > transferencia
            data_coalesce = "COALESCE(data_solicitacao_conv, data_transferencia_conv)"

            query = f"""
            WITH t AS (
                SELECT
                    {col_or_null(c_cod_o, "codigo_assessor_origem")},
                    {col_or_null(c_nome_o, "nome_assessor_origem")},
                    {col_or_null(c_cod_d, "codigo_assessor_destino")},
                    {col_or_null(c_nome_d, "nome_assessor_destino")},
                    {col_or_null(c_solic, "data_solicitacao")},
                    {col_or_null(c_transf, "data_transferencia")},
                    {col_or_null(c_tipo, "tipo")},
                    {col_or_null(c_status, "status")},
                    {c_pl_sql} AS pl,
                    LOWER(TRIM(CAST({c_cliente_sql} AS TEXT))) AS cliente_norm,
                    {solic_conv} AS data_solicitacao_conv,
                    {transf_conv} AS data_transferencia_conv
                FROM {t}
                WHERE {c_pl_sql} IS NOT NULL
                  AND TRIM(CAST({c_pl_sql} AS TEXT)) != ''
                  AND TRIM(CAST({c_pl_sql} AS TEXT)) != '0'
                  {status_where}
            )
            SELECT
                codigo_assessor_origem,
                nome_assessor_origem,
                codigo_assessor_destino,
                nome_assessor_destino,
                data_solicitacao,
                data_transferencia,
                tipo,
                status,
                pl,
                DATE({data_coalesce}) AS data_efetiva
            FROM t
            WHERE cliente_norm = 'externo'
              AND {data_coalesce} IS NOT NULL
              AND DATE({data_coalesce}) BETWEEN '{data_ini_iso}' AND '{data_fim_iso}'
              AND (
                    (codigo_assessor_origem IS NOT NULL AND TRIM(CAST(codigo_assessor_origem AS TEXT)) != '')
                 OR (codigo_assessor_destino IS NOT NULL AND TRIM(CAST(codigo_assessor_destino AS TEXT)) != '')
              )
            ;
            """

            df = pd.read_sql_query(query, conn)

        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def carregar_transferencias_intervalo_sql(data_ini: datetime, data_fim: datetime) -> pd.DataFrame:
    """
    Wrapper: retorna DataFrame tratado (data_efetiva, pl_num, assessor_code)
    usando a lógica SQL (CTE) acima.
    """
    dbp = _find_transfer_db_path()
    if dbp is None:
        return pd.DataFrame()

    data_ini_iso = pd.Timestamp(data_ini).strftime("%Y-%m-%d")
    data_fim_iso = pd.Timestamp(data_fim).strftime("%Y-%m-%d")

    df_raw = _carregar_transferencias_intervalo_sql_cached(
        str(dbp), dbp.stat().st_mtime, data_ini_iso, data_fim_iso
    )
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=["data_efetiva", "pl_num", "assessor_code"])

    out = df_raw.copy()

    # data efetiva já vem como YYYY-MM-DD, mas garante datetime
    out["data_efetiva"] = pd.to_datetime(out.get("data_efetiva"), errors="coerce")

    # pl_num
    out["pl_num"] = _parse_money_like_series(out.get("pl", pd.Series([0] * len(out))))

    # assessor_code: mantém a mesma regra do seu pipeline (destino)
    if "codigo_assessor_destino" in out.columns:
        out["assessor_code"] = out["codigo_assessor_destino"].map(extract_assessor_code)
    else:
        out["assessor_code"] = pd.NA

    out = out.dropna(subset=["data_efetiva"])
    out = out.dropna(subset=["assessor_code"])
    out = out[out["pl_num"] > 0]

    return out[["data_efetiva", "pl_num", "assessor_code"]].copy()


def carregar_transferencias_intervalo_net(data_ini: datetime, data_fim: datetime) -> pd.DataFrame:
    """
    Retorna transferências com sinal:
    +PL quando destino é DBV
    -PL quando origem é DBV
    (usa Data Transferência como prioridade via SQL já corrigido)
    """
    dbp = _find_transfer_db_path()
    if dbp is None:
        return pd.DataFrame(columns=["data_efetiva", "pl_num_signed"])

    data_ini_iso = pd.Timestamp(data_ini).strftime("%Y-%m-%d")
    data_fim_iso = pd.Timestamp(data_fim).strftime("%Y-%m-%d")

    df_raw = _carregar_transferencias_intervalo_sql_cached(
        str(dbp), dbp.stat().st_mtime, data_ini_iso, data_fim_iso
    )
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=["data_efetiva", "pl_num_signed"])

    out = df_raw.copy()
    out["data_efetiva"] = pd.to_datetime(out.get("data_efetiva"), errors="coerce")
    out["pl_num"] = _parse_money_like_series(out.get("pl", pd.Series([0] * len(out))))

    # extrai códigos
    out["cod_origem"] = out.get("codigo_assessor_origem", pd.Series([pd.NA] * len(out))).map(extract_assessor_code)
    out["cod_destino"] = out.get("codigo_assessor_destino", pd.Series([pd.NA] * len(out))).map(extract_assessor_code)

    # define se é DBV (pelo seu mapa)
    dbv_codes = set(ASSESSORES_MAP.keys())

    is_in = out["cod_destino"].isin(dbv_codes)
    is_out = out["cod_origem"].isin(dbv_codes)

    # sinal: entrada +, saída -
    out["pl_num_signed"] = 0.0
    out.loc[is_in, "pl_num_signed"] = out.loc[is_in, "pl_num"]
    out.loc[is_out, "pl_num_signed"] = out.loc[is_out, "pl_num_signed"] - out.loc[is_out, "pl_num"]

    out = out.dropna(subset=["data_efetiva"])
    out = out[out["pl_num_signed"] != 0]

    return out[["data_efetiva", "pl_num_signed"]].copy()


def carregar_transferencias_intervalo(data_ini: datetime, data_fim: datetime) -> pd.DataFrame:
    """
    Carrega e filtra transferências por intervalo de datas.
    Prioridade:
    1) SQL (CTE) com cliente='Externo' + conversão robusta de datas
    2) Fallback: método antigo (carrega tudo e filtra em pandas)
    """
    # 1) Tenta via SQL (novo)
    df_sql = carregar_transferencias_intervalo_sql(data_ini, data_fim)
    if df_sql is not None and not df_sql.empty:
        return df_sql

    # 2) Fallback (se o SQL não achar colunas/tabela compatível)
    df_transf = carregar_dados_transferencias()
    if df_transf is None or df_transf.empty:
        return pd.DataFrame()

    df_transf = tratar_dados_transferencias(df_transf)
    if df_transf is None or df_transf.empty:
        return pd.DataFrame()

    df_transf["data_efetiva"] = pd.to_datetime(df_transf["data_efetiva"], errors="coerce")
    df_transf = df_transf.dropna(subset=["data_efetiva"])

    mask = (df_transf["data_efetiva"] >= data_ini) & (df_transf["data_efetiva"] <= data_fim)
    return df_transf.loc[mask].copy()


def aplicar_transferencias_como_captacao(
    df_pos_f: pd.DataFrame, df_trans: pd.DataFrame, ano_alvo: Optional[int] = None
) -> pd.DataFrame:
    """
    Cria linhas extras de "captação" a partir de transferências (PL),
    para somar automaticamente em rankings (Top 3) sem afetar o cálculo dos KPIs.

    IMPORTANTE:
    - Use esse df APENAS para Top 3 / ranking (não para KPIs),
      pois os KPIs já somam transferências via calcular_captacao_total_liquida().
    """
    if df_pos_f is None or df_pos_f.empty:
        return df_pos_f

    if df_trans is None or df_trans.empty:
        return df_pos_f

    aux = df_trans.copy()
    aux["data_efetiva"] = pd.to_datetime(aux["data_efetiva"], errors="coerce")
    aux = aux.dropna(subset=["data_efetiva"])

    if ano_alvo is None:
        # tenta inferir do df_pos_f (melhor fonte)
        if "Data_Posicao" in df_pos_f.columns:
            dmax = pd.to_datetime(df_pos_f["Data_Posicao"], errors="coerce").dropna()
            if not dmax.empty:
                ano_alvo = int(dmax.max().year)
        if ano_alvo is None:
            ano_alvo = int(aux["data_efetiva"].dt.year.max())

    aux = aux[aux["data_efetiva"].dt.year == int(ano_alvo)]
    if aux.empty:
        return df_pos_f

    df_cap = pd.DataFrame(
        {
            "Data_Posicao": aux["data_efetiva"],
            "Captacao_Liquida_em_M": pd.to_numeric(aux["pl_num"], errors="coerce").fillna(0.0),
            "assessor_code": aux["assessor_code"].astype(str).str.strip(),
            "Net_Em_M": 0.0,
        }
    )

    g = df_cap["assessor_code"].str.upper()
    df_cap = df_cap[~g.isin(["", "NONE", "NENHUM", "NA", "N/A", "NULL", "-", "NAN"])]
    df_cap = df_cap[df_cap["Captacao_Liquida_em_M"] != 0]

    if df_cap.empty:
        return df_pos_f

    return pd.concat([df_pos_f, df_cap], ignore_index=True)


def preparar_df_para_top3_com_transferencias(df_pos_base: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna um DataFrame APENAS para Top 3 (captação) que inclui transferências como captação.
    Não use esse df para KPIs, pois KPIs já somam transferências separadamente.
    """
    if df_pos_base is None or df_pos_base.empty:
        return df_pos_base

    periodos = obter_periodos_referencia(df_pos_base)
    if not periodos:
        return df_pos_base

    # carrega transferências do ano até a data_fim (serve para top3 do ano e do mês,
    # pois o top3 do mês filtra pelo mês internamente)
    df_trans_ytd = carregar_transferencias_intervalo(periodos["ytd_ini"], periodos["data_fim"])
    if df_trans_ytd is None or df_trans_ytd.empty:
        return df_pos_base

    return aplicar_transferencias_como_captacao(
        df_pos_f=df_pos_base,
        df_trans=df_trans_ytd,
        ano_alvo=int(periodos["ano_ref"]),
    )


def _pace_mes_dias_uteis(data_ref_local: pd.Timestamp) -> float:
    """
    Pace do mês por DIAS ÚTEIS (igual seu card).
    Retorna fração 0..1
    """
    data_ref_local = pd.Timestamp(data_ref_local).normalize()
    primeiro = pd.Timestamp(data_ref_local.year, data_ref_local.month, 1)
    ultimo = primeiro + pd.offsets.MonthEnd(1)

    dias_uteis_mes = len(pd.bdate_range(start=primeiro, end=ultimo))
    dias_uteis_corridos = len(pd.bdate_range(start=primeiro, end=data_ref_local))

    if dias_uteis_mes <= 0:
        return 0.0
    return float(dias_uteis_corridos / dias_uteis_mes)


def calcular_captacao_total_liquida(df_pos: pd.DataFrame, data_ini: datetime, data_fim: datetime) -> float:
    """
    Soma captação líquida do Positivador + PL de transferências no intervalo.
    """
    total_pos = 0.0
    if df_pos is not None and not df_pos.empty and {"Data_Posicao", "Captacao_Liquida_em_M"} <= set(df_pos.columns):
        aux = df_pos.copy()
        aux["Data_Posicao"] = pd.to_datetime(aux["Data_Posicao"], errors="coerce")
        aux["Captacao_Liquida_em_M"] = pd.to_numeric(aux["Captacao_Liquida_em_M"], errors="coerce").fillna(0.0)
        m = (aux["Data_Posicao"] >= pd.Timestamp(data_ini)) & (aux["Data_Posicao"] <= pd.Timestamp(data_fim))
        total_pos = float(aux.loc[m, "Captacao_Liquida_em_M"].sum() or 0.0)

    df_trans_net = carregar_transferencias_intervalo_net(data_ini, data_fim)
    total_trans = float(df_trans_net["pl_num_signed"].sum() or 0.0) if not df_trans_net.empty else 0.0

    return total_pos + total_trans


# =====================================================
# OBJETIVOS
# =====================================================
@st.cache_data(show_spinner=False)
def carregar_dados_objetivos_pj1() -> pd.DataFrame:
    caminho_db = Path(__file__).parent.parent / "DBV Capital_Objetivos.db"
    conn = sqlite3.connect(str(caminho_db))
    df = pd.read_sql_query("SELECT * FROM objetivos", conn)
    conn.close()

    if "Objetivo" in df.columns:
        df["Objetivo"] = pd.to_numeric(df["Objetivo"], errors="coerce")

    for c in [
        "auc_objetivo_ano",
        "auc_acumulado",
        "auc_diario_ano",
        "cap_objetivo_ano",
        "cap_acumulado",
        "cap_diario_ano",
        "rec_objetivo_ano",
        "rec_acumulado_ano",
        "rec_diario_ano",
        "c_ativadas_objetivo_ano",
        "c_ativadas_acumulado_ano",
        "c_ativadas_diario_ano",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def obter_meta_objetivo(ano_meta: int, coluna: str, fallback: float = 0.0) -> float:
    """
    Busca um valor de objetivo na tabela objetivos filtrando por ano e coluna.
    """
    try:
        objetivos_df = carregar_dados_objetivos_pj1()
        if objetivos_df.empty:
            return float(fallback)

        col_mapping = {
            "auc_objetivo_ano": "AUC Objetivo",
            "cap_objetivo_ano": "Cap. Liq Objetivo",
            "rec_objetivo_ano": "Receita Objetivo",
            "c_ativadas_objetivo_ano": "Contas Ativadas",
        }
        coluna_real = col_mapping.get(coluna, coluna)

        row_ano = objetivos_df.loc[objetivos_df["Objetivo"] == ano_meta]
        if not row_ano.empty and coluna_real in row_ano.columns:
            val_banco = float(row_ano[coluna_real].max())
            if val_banco > 0:
                if fallback and fallback > val_banco:
                    return float(fallback)
                return val_banco

        return float(fallback)
    except Exception:
        return float(fallback)


@st.cache_data(show_spinner=False)
def carregar_dados_objetivos() -> pd.DataFrame:
    caminho_db = Path(__file__).parent.parent / "DBV Capital_Objetivos.db"
    if not caminho_db.exists():
        caminho_db = Path("DBV Capital_Objetivos.db")

    conn = sqlite3.connect(str(caminho_db))
    try:
        tabs = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            conn,
        )["name"].tolist()

        if not tabs:
            st.error("❌ Nenhuma tabela encontrada no banco de Objetivos.")
            return pd.DataFrame()

        if "objetivos_pj1" in tabs:
            table = "objetivos_pj1"
        elif "objetivos" in tabs:
            table = "objetivos"
        else:
            table = tabs[0]

        df = pd.read_sql_query(f'SELECT * FROM "{table}";', conn)

    except Exception as e:
        st.error(f"Erro ao carregar dados de Objetivos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame(
            {
                "data": [pd.Timestamp.today()],
                "ano": [pd.Timestamp.today().year],
                "auc_total": [1.0],
                "captacao_total_diaria": [1.0],
            }
        )

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.month

    if "auc_objetivo_ano" in df.columns:
        df["auc_total"] = df["auc_objetivo_ano"]

    if "cap_objetivo_ano" in df.columns:
        df["captacao_total_diaria"] = df["cap_objetivo_ano"]

    for col in ["auc_total", "captacao_total_diaria"]:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


# =====================================================
# POSITIVADOR MTD (loader) + NORMALIZAÇÃO
# =====================================================
@st.cache_data(show_spinner=False)
def carregar_dados_positivador_mtd() -> pd.DataFrame:
    base_dir = Path(__file__).parent.parent
    candidate_paths = [
        base_dir / "DBV Capital_Positivador (MTD).db",
        Path("DBV Capital_Positivador (MTD).db"),
        base_dir / "DBV Capital_Positivador_MTD.db",
        Path("DBV Capital_Positivador_MTD.db"),
        base_dir / "DBV Capital_Positivador.db",
        Path("DBV Capital_Positivador.db"),
    ]

    db_path = None
    for p in candidate_paths:
        if p.exists():
            db_path = p
            break

    if db_path is None:
        st.error("❌ Nenhum banco de Positivador encontrado (DBV ou MTD).")
        return pd.DataFrame()

    conn = sqlite3.connect(str(db_path))
    try:
        tabs = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            conn,
        )["name"].tolist()

        if not tabs:
            st.error("❌ Nenhuma tabela encontrada no banco de Positivador.")
            return pd.DataFrame()

        if "positivador" in tabs:
            table = "positivador"
        elif "positivador_mtd" in tabs:
            table = "positivador_mtd"
        else:
            table = tabs[0]

        df = pd.read_sql_query(f'SELECT * FROM "{table}";', conn)
    except Exception as e:
        st.error(f"Erro ao carregar dados do Positivador: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

    return df


def obter_ultima_data_posicao() -> datetime:
    try:
        df = carregar_dados_positivador_mtd()
        if df is None or df.empty:
            st.warning("Nenhum dado encontrado no Positivador MTD. Usando data atual.")
            return datetime.today()

        col_data = None
        # Verifica todas as variantes possíveis do nome da coluna
        for col_name in ["Data_Posição", "Data Posição", "Data_Posicao", "data_posicao"]:
            if col_name in df.columns:
                col_data = col_name
                break

        if col_data is not None:
            if not pd.api.types.is_datetime64_any_dtype(df[col_data]):
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce", dayfirst=True)

            df = df.dropna(subset=[col_data])
            if not df.empty:
                ultima = df[col_data].max()
                if pd.notna(ultima):
                    return ultima.to_pydatetime()

    except Exception as e:
        st.error(f"Erro ao obter a última data do Positivador MTD: {e}")
        st.text(traceback.format_exc())

    st.warning("Usando data atual como fallback para a data de referência.")
    return datetime.today()


def obter_data_atualizacao_positivador() -> datetime:
    return obter_ultima_data_posicao()


def tratar_dados_positivador_mtd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza as colunas do Positivador, aceitando tanto nomes antigos (Excel/Espaços)
    quanto os do novo banco (Underscores).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    renomear = {
        # Padrões com Espaço (Antigo/Excel)
        "Net Em M": "Net_Em_M",
        "Data Posição": "Data_Posicao",
        "data_posicao": "Data_Posicao",
        "Captação Líquida em M": "Captacao_Liquida_em_M",
        "Captação Liq em M": "Captacao_Liquida_em_M",
        "Captacao Liquida em M": "Captacao_Liquida_em_M",
        "Assessor": "assessor",
        "cliente": "Cliente",
        
        # Padrões com Underscore (Banco de Dados Novo)
        "Data_Posição": "Data_Posicao",
        "Data_Posicao": "Data_Posicao",
        "Captação_Líquida_em_M": "Captacao_Liquida_em_M",
        "Captacao_Liquida_Em_M": "Captacao_Liquida_em_M",
        "Data_Atualização": "Data_Atualizacao",
        "Net_Em_M": "Net_Em_M",
        "captacao_liquida_em_m": "Captacao_Liquida_em_M"
    }

    out = df.copy()
    
    # Renomear colunas
    # Usamos um loop para garantir que mesmo variações de case sejam tratadas se necessário,
    # mas o dicionário direto já resolve a maioria.
    out = out.rename(columns=renomear)

    if "Data_Posicao" in out.columns:
        out["Data_Posicao"] = pd.to_datetime(out["Data_Posicao"], errors="coerce", dayfirst=True)

    for c in ["Net_Em_M", "Captacao_Liquida_em_M"]:
        if c in out.columns:
            out[c] = _parse_money_like_series(out[c])
            # Conversão para numérico garantida
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    # Tratamento do código do assessor
    has_assessor_code = "assessor_code" in out.columns
    valid_codes = 0
    if has_assessor_code:
        out["assessor_code"] = out["assessor_code"].astype(str).str.strip()
        valid_codes = int(out["assessor_code"].str.match(r"^A\d{5}$", na=False).sum())

    if (not has_assessor_code) or (valid_codes == 0):
        if "assessor" in out.columns:
            out["assessor"] = out["assessor"].astype(str)
            out["assessor_code"] = out["assessor"].map(extract_assessor_code)
            out["assessor_code"] = out["assessor_code"].where(
                out["assessor_code"].notna() & (out["assessor_code"] != ""), pd.NA
            )
        else:
            out["assessor_code"] = pd.NA
    else:
        out["assessor_code"] = out["assessor_code"].astype(str).str.strip()

    if "Cliente" in out.columns:
        out["Cliente"] = out["Cliente"].astype(str)

    return out


# =====================================================
# NPS / RV - Column mapping
# =====================================================
_EXPECTED_KEYS = {
    "survey_id": {"survey id"},
    "user_id": {"id do usuario", "id usuario", "usuario id"},
    "customer_id": {"costumer id", "customer id", "cliente id"},
    "data_resposta": {"data de resposta", "data resposta", "data"},
    "pesquisa_relacionamento": {"pesquisa relacionamento"},
    "nps_assessor": {"xp relacionamento aniversario nps assessor", "nps assessor"},
    "status": {"status"},
    "codigo_assessor": {"codigo assessor", "cod assessor", "codigo do assessor"},
    "notificacao": {"notificacao", "notificacao ?"},
}
_POSSIBLE_NOTA_KEYS = {
    "nota",
    "nota nps",
    "score",
    "pontuacao",
    "resposta nota",
    "nps",
    "xp relacionamento aniversario nps assessor",
}


def _rename_columns_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    def _norm_key(txt: str) -> str:
        s = _strip_accents(str(txt)).lower()
        s = re.sub(r"[^a-z0-9]+", " ", s).strip()
        return re.sub(r"\s+", " ", s)

    norm_map = {_norm_key(c): c for c in df.columns}
    rename_dict: Dict[str, str] = {}
    for canonical, variants in _EXPECTED_KEYS.items():
        for v in variants:
            if v in norm_map:
                rename_dict[norm_map[v]] = canonical
                break
    df = df.rename(columns=rename_dict)

    nota_col = None
    for c in df.columns:
        if _norm_key(c) in _POSSIBLE_NOTA_KEYS:
            nota_col = c
            break

    if nota_col is None:
        best_col, best_cnt = None, -1
        for c in df.columns:
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().any():
                cnt = int(s.between(0, 10, inclusive="both").sum())
                if cnt > best_cnt and cnt > 0:
                    best_col, best_cnt = c, cnt
        nota_col = best_col

    if nota_col:
        df = df.rename(columns={nota_col: "nota"})

    if "data_resposta" in df.columns:
        df["data_resposta"] = pd.to_datetime(
            df["data_resposta"], errors="coerce", dayfirst=True, infer_datetime_format=True
        )
    if "codigo_assessor" in df.columns:
        df["codigo_assessor"] = df["codigo_assessor"].astype(str).str.strip().str.upper()
    if "pesquisa_relacionamento" in df.columns:
        df["pesquisa_relacionamento_norm"] = _norm_upper_noaccents_series(
            df["pesquisa_relacionamento"]
        )
    if "nota" in df.columns:
        df["nota"] = pd.to_numeric(df["nota"], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def carregar_dados_nps() -> pd.DataFrame:
    try:
        dbp = None
        for p in [
            Path(__file__).parent.parent / "DBV Capital_NPS.db",
            Path("DBV Capital_NPS.db"),
        ]:
            if p.exists():
                dbp = p
                break

        if dbp is None:
            st.error("❌ Banco NPS não encontrado.")
            return pd.DataFrame()

        with sqlite3.connect(str(dbp)) as conn:
            tabs = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
                conn,
            )["name"].tolist()
            if not tabs:
                st.error("❌ Nenhuma tabela encontrada no banco NPS.")
                return pd.DataFrame()

            candidate, best_score = None, -1
            for t in tabs:
                try:
                    df_head = pd.read_sql_query(f'SELECT * FROM "{t}" LIMIT 200;', conn)
                except Exception:
                    continue

                df_norm = _rename_columns_to_canonical(df_head.copy())
                score = (
                    int(
                        "pesquisa_relacionamento" in df_norm.columns
                        or "pesquisa_relacionamento_norm" in df_norm.columns
                    )
                    + int("codigo_assessor" in df_norm.columns)
                    + int("data_resposta" in df_norm.columns)
                    + int("nota" in df_norm.columns)
                )
                if score > best_score:
                    best_score = score
                    candidate = t

            if not candidate:
                candidate = tabs[0]
            df_all = pd.read_sql_query(f'SELECT * FROM "{candidate}";', conn)

        return _rename_columns_to_canonical(df_all)
    except Exception as e:
        st.error(f"Erro ao carregar NPS: {e}")
        return pd.DataFrame()


def _calcular_metricas_nps(df_sub: pd.DataFrame) -> Dict[str, float]:
    total = int(df_sub.shape[0]) if not df_sub.empty else 0
    if total == 0:
        return {
            "total": 0,
            "respondidos": 0,
            "aderencia": 0.0,
            "media": 0.0,
            "nps": 0.0,
            "promotores": 0,
            "neutros": 0,
            "detratores": 0,
        }

    s = pd.to_numeric(df_sub.get("nota"), errors="coerce")
    valid = s.between(0, 10, inclusive="both")
    den = int(valid.sum())

    prom = int(((s >= 9) & (s <= 10) & valid).sum())
    detr = int(((s >= 0) & (s <= 6) & valid).sum())
    neut = int(((s >= 7) & (s <= 8) & valid).sum())

    aderencia = (den / total) * 100.0 if total > 0 else 0.0
    media = float(s[valid].mean()) if den > 0 else 0.0
    nps = 100.0 * (prom / den - detr / den) if den > 0 else 0.0

    return {
        "total": total,
        "respondidos": den,
        "aderencia": aderencia,
        "media": media,
        "nps": nps,
        "promotores": prom,
        "neutros": neut,
        "detratores": detr,
    }


def _top3_assessores_por_aderencia(df_sub: pd.DataFrame) -> pd.DataFrame:
    """
    Top 3 assessores por share de respostas válidas (0-10).
    Retorna DataFrame com colunas: ASSESSOR, ADERENCIA, RESPOSTAS
    """
    assessor_col = next(
        (col for col in ["codigo_assessor", "assessor_code", "assessor"] if col in df_sub.columns), None
    )
    nota_col = next((col for col in ["nota", "rating", "score"] if col in df_sub.columns), None)

    if df_sub is None or df_sub.empty or not assessor_col or not nota_col:
        return pd.DataFrame(columns=["ASSESSOR", "ADERENCIA", "RESPOSTAS"])

    df = df_sub.copy()
    s_nota = pd.to_numeric(df[nota_col], errors="coerce")
    df["_valid"] = s_nota.between(0, 10, inclusive="both")
    total_validos = float(df["_valid"].sum())

    agg = (
        df[df["_valid"]]
        .groupby(assessor_col)
        .agg(total_respostas=(nota_col, "size"), respondidos=("_valid", "sum"))
        .reset_index()
    )

    agg["share"] = (agg["respondidos"] / total_validos * 100.0) if total_validos > 0 else 0.0
    agg = agg.sort_values(["respondidos", "share"], ascending=[False, False]).head(3)

    out = agg[[assessor_col, "share", "respondidos"]].rename(
        columns={assessor_col: "ASSESSOR", "respondidos": "RESPOSTAS", "share": "ADERENCIA"}
    )
    return out[["ASSESSOR", "ADERENCIA", "RESPOSTAS"]]


# =====================================================
# AUC mesa RV (mantido)
# =====================================================
def _parse_money_series_rv(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)

    def conv(x: str) -> Any:
        if x in ("", "nan", "NaN", "None"):
            return np.nan
        if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", x):
            return float(x.replace(".", "").replace(",", "."))
        if re.match(r"^\d{1,3}(,\d{3})+(\.\d+)?$", x):
            return float(x.replace(",", ""))
        if "," in x and "." not in x:
            return float(x.replace(",", "."))
        return float(x)

    out = s.map(lambda v: conv(v) if v not in (None, "") else None)
    return pd.to_numeric(out, errors="coerce").fillna(0.0)


def _find_auc_db_path() -> Optional[Path]:
    for p in [
        Path(__file__).parent.parent / "DBV Capital_AUC Mesa RV.db",
        Path("DBV Capital_AUC Mesa RV.db"),
    ]:
        if p.exists():
            return p
    return None


@st.cache_data(show_spinner=False)
def _load_auc_table(db_path: Path) -> pd.DataFrame:
    if not db_path or not Path(db_path).exists():
        return pd.DataFrame()
    with sqlite3.connect(str(db_path)) as conn:
        tabs = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            conn,
        )["name"].tolist()
        table = "auc_mesa_rv" if "auc_mesa_rv" in tabs else (tabs[0] if tabs else None)
        if not table:
            return pd.DataFrame()
        df = pd.read_sql_query(f'SELECT * FROM "{table}";', conn)

    cols = {c.lower(): c for c in df.columns}
    c_data = cols.get("data")
    c_cli = cols.get("cliente")
    c_ass = cols.get("assessor")
    c_tipo = cols.get("tipo")
    c_auc = cols.get("auc")

    out = pd.DataFrame()
    out["data_parsed"] = pd.to_datetime(df[c_data], dayfirst=True, errors="coerce") if c_data else pd.NaT
    out["cliente"] = df[c_cli].astype(str).str.strip() if c_cli else ""
    out["assessor"] = df[c_ass].astype(str).str.strip() if c_ass else ""
    out["tipo"] = df[c_tipo].astype(str).str.strip() if c_tipo else ""
    out["auc_reais"] = _parse_money_series_rv(df[c_auc]) if c_auc else 0.0
    out = out.dropna(subset=["data_parsed"])
    return out


# =====================================================
# KPIs Objetivos (Captação / AUC)
# =====================================================
def calcular_indicadores_objetivos(
    df_pos: pd.DataFrame, df_obj: pd.DataFrame, hoje: datetime, df_pos_ytd: Optional[pd.DataFrame] = None
) -> Dict[str, Dict[str, Any]]:
    with st.sidebar.expander("🔍 Debug - Entrada calcular_indicadores_objetivos", expanded=False):
        st.write("### Dados de Entrada")
        st.json(
            {
                "df_pos_shape": df_pos.shape if hasattr(df_pos, "shape") else "N/A",
                "df_pos_columns": list(df_pos.columns) if hasattr(df_pos, "columns") else "N/A",
                "df_obj_shape": df_obj.shape if hasattr(df_obj, "shape") else "N/A",
                "hoje": str(hoje),
            }
        )

        if hasattr(df_pos, "columns"):
            st.write("### Colunas no DataFrame de Posição")
            st.write(", ".join(df_pos.columns))

            if "Data_Posicao" in df_pos.columns:
                st.write("### Período dos Dados")
                st.write(f"- Primeira data: {df_pos['Data_Posicao'].min()}")
                st.write(f"- Última data: {df_pos['Data_Posicao'].max()}")

            numeric_cols = df_pos.select_dtypes(include=["number"]).columns.tolist()
            st.write("### Colunas Numéricas")
            st.write(", ".join(numeric_cols) if numeric_cols else "Nenhuma coluna numérica encontrada")

    hoje = pd.Timestamp(hoje or pd.Timestamp.today()).normalize()
    ano_atual = hoje.year

    if df_pos is None or df_pos.empty:
        st.sidebar.error("⚠️ Dados do Positivador vazios ou inválidos")
        return {}

    df_pos = df_pos.copy()
    df_pos_ytd = df_pos_ytd if (df_pos_ytd is not None and not df_pos_ytd.empty) else df_pos
    df_pos_ytd = df_pos_ytd.copy()
    st.sidebar.write("🔍 Colunas disponíveis no DataFrame:", ", ".join(df_pos.columns.tolist()))

    if "Data_Posicao" in df_pos.columns:
        df_pos["Data_Posicao"] = pd.to_datetime(df_pos["Data_Posicao"], errors="coerce", dayfirst=True)
        if df_pos["Data_Posicao"].isna().any():
            st.sidebar.warning(f"⚠️ {df_pos['Data_Posicao'].isna().sum()} datas inválidas encontradas")

    for col in ["Net_Em_M", "Captacao_Liquida_em_M"]:
        if col in df_pos.columns:
            if not pd.api.types.is_numeric_dtype(df_pos[col]):
                df_pos[col] = _parse_money_like_series(df_pos[col])
                zeros = int((df_pos[col] == 0).sum())
                if zeros > 0:
                    st.sidebar.warning(f"⚠️ {zeros} valores zerados em {col} (após conversão)")

            df_pos[col] = pd.to_numeric(df_pos[col], errors="coerce").fillna(0.0)
            st.sidebar.write(
                f"📊 {col} - Média: {df_pos[col].mean():.2f}, Mín: {df_pos[col].min():.2f}, Máx: {df_pos[col].max():.2f}"
            )

    periodos = obter_periodos_referencia(df_pos)
    if periodos is None:
        st.sidebar.warning("⚠️ Não foi possível determinar os períodos de referência")
        return {}

    data_ref_local = periodos["data_fim"]
    mesref_pos = pd.Period(year=data_ref_local.year, month=data_ref_local.month, freq="M")

    capliq_mes_atual = 0.0
    try:
        capliq_mes_atual = calcular_captacao_total_liquida(df_pos, periodos["mtd_ini"], periodos["data_fim"])
    except Exception as e:
        st.sidebar.error(f"Erro ao calcular captação mensal: {str(e)}")

    pace_mes = None
    try:
        pace_mes = _pace_mes_dias_uteis(data_ref_local)
    except Exception as e:
        st.sidebar.warning(f"⚠️ Erro ao calcular pace do mês (dias úteis): {str(e)}")

    capliq_ano_atual = 0.0
    try:
        st.sidebar.write("🔍 Calculando captação anual (YTD):")
        st.sidebar.write(f"   - Data inicial: {periodos['ytd_ini'].strftime('%d/%m/%Y')}")
        st.sidebar.write(f"   - Data final: {periodos['data_fim'].strftime('%d/%m/%Y')}")

        mask_ytd = (df_pos_ytd["Data_Posicao"] >= periodos["ytd_ini"]) & (df_pos_ytd["Data_Posicao"] <= periodos["data_fim"])
        captacao_ytd_pos = float(df_pos_ytd.loc[mask_ytd, "Captacao_Liquida_em_M"].sum() or 0.0)
        st.sidebar.write(f"   - Captação Positivador YTD (FULL): R$ {captacao_ytd_pos:,.2f} Mi")

        capliq_ano_atual = calcular_captacao_total_liquida(df_pos_ytd, periodos["ytd_ini"], periodos["data_fim"])
        st.sidebar.write(f"   - Captação Total (com transferências): R$ {capliq_ano_atual:,.2f} Mi")
    except Exception as e:
        st.sidebar.error(f"Erro ao calcular captação anual: {str(e)}")
        st.sidebar.error(f"Detalhes do erro: {traceback.format_exc()}")

    cap_meta_eoy = 0.0
    cap_meta_hoje = 0.0
    try:
        df_pj1 = carregar_dados_objetivos_pj1()
        if not df_pj1.empty and "Objetivo" in df_pj1.columns:
            base = df_pj1[df_pj1["Objetivo"] == ano_atual].copy()
            if not base.empty and "Cap. Liq Objetivo" in base.columns:
                cap_meta_eoy = float(base["Cap. Liq Objetivo"].max())
                dias_decorridos = (hoje - pd.Timestamp(ano_atual, 1, 1)).days + 1
                total_dias_ano = 366 if pd.Timestamp(ano_atual, 12, 31).dayofyear == 366 else 365
                cap_meta_hoje = (cap_meta_eoy * dias_decorridos) / total_dias_ano
    except Exception:
        cap_meta_hoje = 0.0
        cap_meta_eoy = 0.0

    df_obj = df_obj.copy()
    if "Objetivo" in df_obj.columns:
        df_obj["Objetivo"] = pd.to_numeric(df_obj["Objetivo"], errors="coerce")

    objetivo_anual = 0.0
    if "Cap. Liq Objetivo" in df_obj.columns and not df_obj.empty:
        obj_ano = df_obj[df_obj["Objetivo"] == ano_atual]
        objetivo_anual = float(obj_ano["Cap. Liq Objetivo"].max()) if not obj_ano.empty else float(df_obj["Cap. Liq Objetivo"].max())

    valor_alcancado_ano = capliq_ano_atual
    mes_atual = hoje.month
    obj_restante_ano = max(0.0, (objetivo_anual or 0.0) - valor_alcancado_ano)
    meses_restantes = max(1, 12 - mes_atual + 1)
    obj_capliq_mes_max = obj_restante_ano / meses_restantes

    auc_meta_eoy = 0.0
    auc_meta_hoje = 0.0
    try:
        df_pj1 = carregar_dados_objetivos_pj1()
        if not df_pj1.empty and "Objetivo" in df_pj1.columns:
            base_auc = df_pj1[df_pj1["Objetivo"] == ano_atual].copy()
            if not base_auc.empty and "AUC Objetivo" in base_auc.columns:
                auc_meta_eoy = float(base_auc["AUC Objetivo"].max())
                dias_decorridos = (hoje - pd.Timestamp(ano_atual, 1, 1)).days + 1
                total_dias_ano = 366 if pd.Timestamp(ano_atual, 12, 31).dayofyear == 366 else 365
                auc_meta_hoje = (auc_meta_eoy * dias_decorridos) / total_dias_ano
    except Exception:
        pass

    auc_atual = 0.0
    if (mesref_pos is not None) and {"Data_Posicao", "Net_Em_M"} <= set(df_pos.columns):
        mask_mesrec = df_pos["Data_Posicao"].dt.to_period("M") == mesref_pos
        auc_atual = float(df_pos.loc[mask_mesrec, "Net_Em_M"].sum() or 0.0)

    return {
        "capliq_mes": {
            "valor": capliq_mes_atual,
            "max": obj_capliq_mes_max,
            "pace_target": (obj_capliq_mes_max * pace_mes) if (pace_mes is not None and obj_capliq_mes_max is not None) else None,
            "mesref": str(mesref_pos) if mesref_pos is not None else "-",
        },
        "capliq_ano": {
            "valor": capliq_ano_atual,
            "max": cap_meta_eoy,
            "pace_target": cap_meta_hoje,
            "ano": ano_atual,
        },
        "auc": {
            "valor": auc_atual,
            "max": auc_meta_eoy,
            "pace_target": auc_meta_hoje,
            "mesref": str(mesref_pos) if mesref_pos is not None else "-",
        },
    }


# =====================================================
# Render Helpers (progress, top3, etc.) - mantidos
# =====================================================
def obter_auc_inicial_ano(df: pd.DataFrame, ano: int) -> float:
    if df is None or df.empty:
        return 0.0
    if "Data_Posicao" not in df.columns or "Net_Em_M" not in df.columns:
        return 0.0

    aux = df.copy()
    aux["Data_Posicao"] = pd.to_datetime(aux["Data_Posicao"], errors="coerce")
    aux = aux[aux["Data_Posicao"].dt.year == ano]
    if aux.empty:
        return 0.0

    primeira_data = aux["Data_Posicao"].min()
    return float(aux.loc[aux["Data_Posicao"] == primeira_data, "Net_Em_M"].sum() or 0.0)


AUC_BASE_2025 = obter_auc_inicial_ano(df_positivador, 2025) if "df_positivador" in globals() else 0.0


def render_custom_progress_bars(
    objetivo_hoje_val: float, realizado_val: float, max_val: float, min_val: float = 0
) -> None:
    objetivo_hoje_raw = float(objetivo_hoje_val or 0.0)
    realizado_raw = float(realizado_val or 0.0)
    min_val = float(min_val or 0.0)
    max_val = float(max_val or 0.0)

    if max_val <= min_val:
        max_val = min_val + 1.0

    range_val = max(max_val - min_val, 0.01)

    objetivo_plot = min(max(objetivo_hoje_raw - min_val, 0.0), range_val)
    realizado_plot = min(max(realizado_raw - min_val, 0.0), range_val)

    projetado_pct = (objetivo_plot / range_val) * 100.0
    realizado_pct = (realizado_plot / range_val) * 100.0

    fmt_max = formatar_valor_curto(max_val)
    fmt_projetado = formatar_valor_curto(objetivo_hoje_raw) if objetivo_hoje_raw > 0 else ""
    fmt_realizado = formatar_valor_curto(realizado_raw) if realizado_raw != 0 else ""

    html_bars = f"""
<div class="progress-wrapper">
  <div class="progress-container">
    <div class="progress-label" style="font-weight: bold;">PROJETADO</div>
    <div class="progress-bar-track">
      <div class="progress-bar-fill" style="width: {projetado_pct:.2f}%;"></div>
      <span class="progress-bar-limit-label right">{fmt_max}</span>
      <span class="progress-bar-value-label">{fmt_projetado}</span>
    </div>
  </div>

  <div class="progress-container">
    <div class="progress-label" style="font-weight: bold;">REALIZADO</div>
    <div class="progress-bar-track">
      <div class="progress-bar-fill" style="width: {realizado_pct:.2f}%;"></div>
      <span class="progress-bar-limit-label right">{fmt_max}</span>
      <span class="progress-bar-value-label">{fmt_realizado}</span>
    </div>
  </div>
</div>
"""
    st.markdown(dedent(html_bars), unsafe_allow_html=True)


def top3_mes_cap(
    df: pd.DataFrame,
    date_col: str = "Data_Posicao",
    value_col: str = "Captacao_Liquida_em_M",
    group_col: str = "assessor_code",
) -> Tuple[List[Tuple[str, float]], str]:
    req = {date_col, value_col}
    if date_col not in df.columns:
        return [], "-"

    if group_col not in df.columns:
        if "assessor" in df.columns:
            group_col = "assessor"
        else:
            return [], "-"

    req.add(group_col)
    if not req <= set(df.columns):
        return [], "-"

    dfx = df[list(req)].copy()
    dfx[date_col] = pd.to_datetime(dfx[date_col], errors="coerce")
    dfx[value_col] = pd.to_numeric(dfx[value_col], errors="coerce").fillna(0)
    dfx[group_col] = dfx[group_col].astype(str).str.strip()

    gnorm = dfx[group_col].str.upper()
    invalid = gnorm.isin(["", "NONE", "NENHUM", "NA", "N/A", "NULL", "-", "NAN"])
    dfx = dfx[~invalid]
    dfx = dfx[dfx[value_col] != 0]

    if dfx.empty:
        return [], "-"

    per_valid = dfx[date_col].dt.to_period("M").dropna()
    if per_valid.empty:
        return [], "-"

    mesref = per_valid.max()
    dmes = dfx[dfx[date_col].dt.to_period("M") == mesref]
    if dmes.empty:
        return [], str(mesref)

    serie = dmes.groupby(group_col)[value_col].sum().sort_values(ascending=False)
    return list(serie.items())[:5], str(mesref)


def top3_ano_cap(
    df: pd.DataFrame,
    date_col: str = "Data_Posicao",
    value_col: str = "Captacao_Liquida_em_M",
    group_col: str = "assessor_code",
) -> Tuple[List[Tuple[str, float]], str]:
    req = {date_col, value_col}
    if date_col not in df.columns:
        return [], "-"

    if group_col not in df.columns:
        if "assessor" in df.columns:
            group_col = "assessor"
        else:
            return [], "-"

    req.add(group_col)
    if not req <= set(df.columns):
        return [], "-"

    dfx = df[list(req)].copy()
    dfx[date_col] = pd.to_datetime(dfx[date_col], errors="coerce")
    dfx[value_col] = pd.to_numeric(dfx[value_col], errors="coerce").fillna(0)
    dfx[group_col] = dfx[group_col].astype(str).str.strip()

    gnorm = dfx[group_col].str.upper()
    invalid = gnorm.isin(["", "NONE", "NENHUM", "NA", "N/A", "NULL", "-", "NAN"])
    dfx = dfx[~invalid]
    dfx = dfx[dfx[value_col] != 0]

    if dfx.empty:
        return [], "-"

    anos = dfx[date_col].dt.year.dropna().astype(int).unique()
    if len(anos) == 0:
        return [], "-"

    ano = int(sorted(anos)[-1])
    dane = dfx[dfx[date_col].dt.year == ano]
    if dane.empty:
        return [], str(ano)

    serie = dane.groupby(group_col)[value_col].sum().sort_values(ascending=False)
    return list(serie.items())[:5], str(ano)


def _render_top3_horizontal(items: List[Tuple[str, float]], header_text: str) -> None:
    if not items:
        st.markdown(
            "<div class='table-container'><p style='padding:12px'>Sem dados.</p></div>",
            unsafe_allow_html=True,
        )
        return

    top3 = items[:3]
    nomes_curto = []
    for ass, _ in top3:
        full = obter_nome_assessor(ass) if ass else "-"
        nomes_curto.append(_primeiro_nome_sobrenome(full))

    css = """
    <style>
      .top3-h-wrap {
        border: 1.8px solid rgba(46, 204, 113, 0.85);
        border-radius: 14px;
        background: linear-gradient(180deg, rgba(46,204,113,0.15) 0%, rgba(46,204,113,0.06) 100%);
        padding: 10px 14px 8px 14px;
        max-width: var(--tv-block-width, 680px);
        width: 100%;
        margin: 16px auto 0 auto;
        box-shadow: 0 3px 10px rgba(0,0,0,0.22);
      }
      .top3-h-title {
        text-align: center;
        font-weight: 800;
        color: #fff;
        margin: 0 0 6px 0;
        letter-spacing: 0.4px;
        font-size: 1.05em;
      }
      .top3-v-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .top3-v-item {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px 10px;
        border-radius: 10px;
        font-weight: 800;
        color: #ffffff;
        font-size: 0.88em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;
        min-height: 32px;
      }
      .top3-v-medal { width:30px; flex-shrink:0; text-align:right; margin-right: 5px; }
      .top3-v-name { flex:1; text-align:center; padding-left: 0; margin-left: -20px; }
      .top3-v-item.pos-1 { background: linear-gradient(135deg, rgba(255,213,79,.15), rgba(46,204,113,.03)); }
      .top3-v-item.pos-2 { background: linear-gradient(135deg, rgba(207,216,220,.15), rgba(46,204,113,.03)); }
      .top3-v-item.pos-3 { background: linear-gradient(135deg, rgba(255,171,145,.15), rgba(46,204,113,.03)); }
    </style>
    """

    medals = ["🥇", "🥈", "🥉"]
    rows_html = []
    for i, nome in enumerate(nomes_curto, start=1):
        medal = medals[i - 1]
        rows_html.append(
            f"<div class='top3-v-item pos-{i}'>"
            f"<span class='top3-v-medal'>{medal} {i}</span>"
            f"<span class='top3-v-name'>{nome}</span>"
            f"</div>"
        )

    html = f"""
    {css}
    <div class="top3-h-wrap">
      <div class="top3-h-title">{header_text}</div>
      <div class="top3-v-list">
        {''.join(rows_html)}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# =====================================================
# FUNÇÃO RUMO A 1BI (mantida; depende de df_pos_f/df_obj/data_ref)
# =====================================================
def render_rumo_a_1bi(auc_base_inicial_2025: float = 0.0):
    """
    Renderiza o painel 'Rumo a 1BI' na coluna atual.
    """
    OBJETIVO_FINAL = obter_meta_objetivo(2027, "auc_objetivo_ano", 1_000_000_000.0)

    v_auc = 0.0
    try:
        mets_local = calcular_indicadores_objetivos(df_pos_f, df_obj, hoje=data_ref)
        if "auc" in mets_local and "valor" in mets_local["auc"]:
            v_auc = float(mets_local["auc"]["valor"] or 0.0)
    except Exception as e:
        st.error(f"Erro ao carregar o AUC atual: {e}")
        v_auc = 0.0

    data_atualizacao = pd.Timestamp(data_ref)

    meta_2025 = obter_meta_objetivo(2025, "auc_objetivo_ano", 600_000_000.0)
    meta_2026 = obter_meta_objetivo(2026, "auc_objetivo_ano", 800_000_000.0)
    meta_2027 = OBJETIVO_FINAL

    meta_2025 = max(0.0, min(meta_2025, meta_2026, meta_2027))
    meta_2026 = max(meta_2025, min(meta_2026, meta_2027))
    meta_2027 = max(meta_2026, meta_2027)

    d0 = pd.Timestamp(2025, 1, 1)
    d1 = pd.Timestamp(2025, 12, 31)
    d2 = pd.Timestamp(2026, 12, 31)
    d3 = pd.Timestamp(2027, 12, 31)

    v0, v1, v2, v3 = 0.0, meta_2025, meta_2026, meta_2027

    def _interp_linear(data, di, df, vi, vf) -> float:
        if data <= di:
            return float(vi)
        if data >= df:
            return float(vf)
        total = (df - di).days
        if total <= 0:
            return float(vf)
        decorrido = (data - di).days
        return float(vi + (vf - vi) * (decorrido / total))

    if data_atualizacao < d0:
        threshold_projetado = 0.0
    elif data_atualizacao <= d1:
        try:
            mets_auc = calcular_indicadores_objetivos(df_pos_f, df_obj, hoje=data_atualizacao)
            if "auc" in mets_auc and "pace_target" in mets_auc["auc"]:
                threshold_projetado = float(mets_auc["auc"]["pace_target"])
            else:
                threshold_projetado = _interp_linear(data_atualizacao, d0, d1, v0, v1)
        except Exception:
            threshold_projetado = _interp_linear(data_atualizacao, d0, d1, v0, v1)
    elif data_atualizacao <= d2:
        threshold_projetado = _interp_linear(data_atualizacao, d1, d2, v1, v2)
    elif data_atualizacao <= d3:
        threshold_projetado = _interp_linear(data_atualizacao, d2, d3, v2, v3)
    else:
        threshold_projetado = float(meta_2027)

    pct_auc = (v_auc / OBJETIVO_FINAL) * 100 if OBJETIVO_FINAL > 0 else 0
    restante_auc = max(0.0, OBJETIVO_FINAL - v_auc)
    dias_restantes = max(0, (d3 - data_atualizacao).days)

    diff_pace = v_auc - threshold_projetado
    pct_diff_pace = (diff_pace / threshold_projetado * 100) if threshold_projetado > 0 else 0

    if diff_pace >= 0:
        diff_text = f"<span style='color:#2ecc7a'>{fmt_valor(diff_pace)} ({pct_diff_pace:+.1f}%) 🎯</span>"
        border_style = "border-left-color: #2ecc7a !important;"
    else:
        diff_text = f"<span style='color:#e74c3c'>{fmt_valor(diff_pace)} ({pct_diff_pace:+.1f}%)</span>"
        border_style = "border-left-color: #e74c3c !important;"

    fmt_objetivo_final = formatar_valor_curto(OBJETIVO_FINAL)
    st.markdown(
        f"""
        <div class='objetivo-card-topo'>
          <span>Objetivo Total (2027):</span>
          <span class='valor'>{fmt_objetivo_final}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_custom_progress_bars(
        objetivo_hoje_val=threshold_projetado,
        realizado_val=v_auc,
        max_val=OBJETIVO_FINAL,
        min_val=0,
    )

    cards_rumo_html = f"""
    <div class="tv-metric-grid">
      <div class="metric-pill metric-pill-top"
           style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
        <div class="label" style="font-size: 11px;">Dias Restantes</div>
        <div class="value" style="font-size: 0.9rem;">{dias_restantes}</div>
      </div>

      <div class="metric-pill metric-pill-top"
           style="{border_style} min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
        <div class="label" style="font-size: 11px;">Projetado vs Realizado</div>
        <div class="value" style="font-size: 0.8rem; line-height: 1.2;">
          {diff_text}
        </div>
      </div>

      <div class="metric-pill metric-pill-top"
           style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
        <div class="label" style="font-size: 11px; white-space: nowrap;">Percentual Realizado</div>
        <div class="value" style="font-size: 0.9rem; font-weight: bold;">
          {fmt_pct(pct_auc/100)}
        </div>
      </div>

      <div class="metric-pill metric-pill-top"
           style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
        <div class="label" style="font-size: 11px; white-space: nowrap;">Valor Restante</div>
        <div class="value" style="font-size: 0.9rem; font-weight: bold;">
          <span style="color:white">{fmt_valor(restante_auc)}</span>
        </div>
      </div>
    </div>
    """
    st.markdown(cards_rumo_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    items_rumo_auc, _ = top3_mes_cap(df_pos_f, value_col="Net_Em_M")
    _render_top3_horizontal(items_rumo_auc, header_text="Top 3 — AUC")


# =====================================================
# EXECUÇÃO PRINCIPAL - LOADS
# =====================================================
with st.spinner("Carregando dados..."):
    try:
        # Carregar dados MTD
        st.sidebar.write("🔍 Carregando dados do Positivador MTD...")
        df_pos_raw = carregar_dados_positivador_mtd()

        if df_pos_raw is None or df_pos_raw.empty:
            st.error("❌ Dados do Positivador MTD estão vazios ou não puderam ser carregados")
            st.stop()

        st.sidebar.write(f"📊 Dados MTD brutos carregados: {len(df_pos_raw)} linhas, {len(df_pos_raw.columns)} colunas")

        st.sidebar.write("✅ Processando dados MTD...")
        df_pos = tratar_dados_positivador_mtd(df_pos_raw)

        if df_pos is None or df_pos.empty:
            st.error("❌ Dados processados do Positivador MTD estão vazios")
            st.stop()

        st.sidebar.write(f"✅ Dados MTD processados: {len(df_pos)} linhas")

        # Carregar dados FULL para YTD
        st.sidebar.write("🔍 Carregando dados do Positivador FULL (YTD)...")
        _pos_full_path = Path(__file__).parent.parent / "DBV Capital_Positivador.db"
        if _pos_full_path.exists():
            df_pos_full = carregar_dados_positivador(str(_pos_full_path), _pos_full_path.stat().st_mtime)
            st.sidebar.write(f"✅ Dados FULL carregados: {len(df_pos_full) if df_pos_full is not None else 0} linhas")
        else:
            df_pos_full = None
            st.sidebar.warning("⚠️ Arquivo do Positivador FULL não encontrado. Usando MTD para YTD.")

        # Se não encontrou o FULL, usa o MTD como fallback
        if df_pos_full is None or df_pos_full.empty:
            df_pos_full = df_pos.copy()
            st.sidebar.warning("⚠️ Dados FULL vazios. Usando MTD para YTD.")
        else:
            # Aplicar mesmo tratamento dos dados MTD
            df_pos_full = tratar_dados_positivador_mtd(df_pos_full)
            st.sidebar.write(f"✅ Dados FULL processados: {len(df_pos_full)} linhas")

        st.sidebar.write("🔍 Carregando dados de objetivos...")
        df_obj = carregar_dados_objetivos()

        if df_obj is None or df_obj.empty:
            st.warning("⚠️ Dados de objetivos estão vazios")
        else:
            st.sidebar.write(f"✅ Dados de objetivos carregados: {len(df_obj)} linhas")

    except Exception as e:
        st.error(f"❌ Erro ao carregar bases de dados: {e}")
        st.text(traceback.format_exc())
        st.stop()

if df_pos.empty:
    st.error("❌ Sem dados no Positivador MTD após processamento")
    st.stop()

if df_obj is None or df_obj.empty:
    st.warning("⚠️ Dados de objetivos não encontrados. Algumas métricas podem não ser exibidas.")

df_pos_f = df_pos.copy()

# --- Positivador FULL (DB completo) para YTD ---
_pos_full_path = Path(__file__).parent.parent / "DBV Capital_Positivador.db"
df_pos_full = (
    carregar_dados_positivador(str(_pos_full_path), _pos_full_path.stat().st_mtime)
    if _pos_full_path.exists()
    else pd.DataFrame()
)

# normaliza (garante colunas e tipos)
if df_pos_full is not None and not df_pos_full.empty:
    if "Data_Posicao" in df_pos_full.columns:
        df_pos_full["Data_Posicao"] = pd.to_datetime(df_pos_full["Data_Posicao"], errors="coerce")
    if "Captacao_Liquida_em_M" in df_pos_full.columns:
        df_pos_full["Captacao_Liquida_em_M"] = pd.to_numeric(df_pos_full["Captacao_Liquida_em_M"], errors="coerce").fillna(0.0)

# DataFrame auxiliar APENAS para Top 3 (captação) incluindo transferências como captação
df_pos_mes_cap_top3 = preparar_df_para_top3_com_transferencias(df_pos_f)  # MTD para ranking do mês
df_pos_ano_cap_top3 = preparar_df_para_top3_com_transferencias(df_pos_full)  # FULL para ranking do ano

data_atualizacao_bd = obter_ultima_data_posicao()
data_ref = pd.Timestamp(data_atualizacao_bd).normalize()
data_formatada = data_ref.strftime("%d/%m/%Y")

# =====================================================
# DEBUG — Captação (Positivador) x Transferências (PL)
# =====================================================

with st.sidebar.expander("📌 Amostra dos Dados", expanded=False):
    st.write("### Dados do Positivador (5 primeiras linhas)")
    st.dataframe(df_pos_f.head())

# =====================================================
# HEADER / CONTAINER
# =====================================================
st.markdown(
    """
<style>
:root {
    --radius: 20px;
    --border-width: 1px;
    --border-color: #d1d9d5;
    --tv-block-width: 100%;
    --page-bg: #20352F;
}

.dbv-dashboard-root {
    max-width: 100%;
    margin: 0;
    padding-bottom: 0;
    display: flex;
    flex-direction: column;
    gap: calc(18px * var(--tv-scale));
}

/* Wrapper principal - sem transform para ocupar 100% da tela */
div[data-testid="stVerticalBlock"]:has(.painel-tv-sentinel) {
    width: 100% !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

.dashboard-card.nps-card {
    height: 440px !important;
    min-height: 440px !important;
    max-height: 440px !important;
    margin-top: 0 !important;
}

.stPlotlyChart {
    height: 440px !important;
    min-height: 440px !important;
    max-height: 440px !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    margin-top: 0 !important;
}

.tv-metric-grid {
    height: 120px !important;
    min-height: 120px !important;
    margin-bottom: 0px !important;
}

.ranking-table { font-size: 1.05em !important; }
.ranking-table th { font-size: 0.95em !important; padding: 6px 4px !important; }
.ranking-table td { padding: 6px 4px !important; }

.gradient-text {
    background: linear-gradient(90deg, #ffffff, #e0e0e0, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-fill-color: transparent;
    display: inline-block;
    margin: 0;
    line-height: 1;
}
</style>
""",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='dbv-dashboard-root'>", unsafe_allow_html=True)

    header_html = """
    <div style='text-align: center; margin: 0 auto; width: 100%; max-width: 500px; padding: 10px 0 2px 0;'>
        <div style='margin: 2px 0 8px 0; text-align: center;'>
            <span style='font-size: 1.1rem; color: #2ecc71; font-weight: 600; display: inline-block;'>
                Atualizado em: <strong>__DATA_ATUALIZACAO__</strong>
            </span>
        </div>
    </div>
    """
    st.markdown(header_html.replace("__DATA_ATUALIZACAO__", data_formatada), unsafe_allow_html=True)
    st.markdown("<div class='painel-tv-sentinel'></div>", unsafe_allow_html=True)


    # =====================================================
    # SEÇÃO SUPERIOR: GRÁFICO + NPS
    # =====================================================
    col_upper_left, col_upper_right = st.columns([2, 1], gap="small")

    with col_upper_left:
        if not df_positivador.empty:
            df_positivador["ano_mes"] = df_positivador["Data_Posicao"].dt.strftime("%Y-%m")
            df_auc_mensal = df_positivador.groupby("ano_mes")["Net_Em_M"].sum().reset_index()

            df_clientes_positivo = (
                df_positivador[df_positivador["Net_Em_M"] > 0]
                .groupby("ano_mes")
                .size()
                .reset_index(name="clientes_positivo")
            )

            df_growth_auc = pd.merge(df_auc_mensal, df_clientes_positivo, on="ano_mes", how="outer").fillna(0)
            df_growth_auc["data"] = pd.to_datetime(df_growth_auc["ano_mes"] + "-01")
            df_growth_auc = df_growth_auc.sort_values("data")

            # =========================
            # KPIs do ponto MAIS RECENTE do gráfico
            # =========================
            ultima = df_growth_auc.iloc[-1] if not df_growth_auc.empty else None
            auc_hoje = float(ultima.get("Net_Em_M", 0.0) or 0.0) if ultima is not None else 0.0
            clientes_ativos_hoje = int(ultima.get("clientes_positivo", 0) or 0) if ultima is not None else 0
            auc_hoje_txt = formatar_valor_curto(auc_hoje)
            clientes_hoje_txt = f"{clientes_ativos_hoje:,}".replace(",", ".")

            min_auc = float(df_growth_auc["Net_Em_M"].min() or 0.0)
            max_auc = float(df_growth_auc["Net_Em_M"].max() or 0.0)
            if max_auc <= min_auc:
                max_auc = min_auc + 50_000_000

            nice_min = math.floor(min_auc / 50_000_000.0) * 50_000_000.0
            nice_max = math.ceil(max_auc / 50_000_000.0) * 50_000_000.0
            nice_max = max(nice_max, max_auc * 1.05)

            dtick_val = 50_000_000
            tick_vals = list(np.arange(nice_min, nice_max + dtick_val, dtick_val))
            tick_text = [f"R$ {int(v / 1_000_000)}M" for v in tick_vals]

            fig_growth_auc = go.Figure()
            
            fig_growth_auc.add_trace(
                go.Bar(
                    x=df_growth_auc["ano_mes"],
                    y=df_growth_auc["clientes_positivo"],
                    name="Clientes Ativos",
                    marker_color="#948161",
                    opacity=0.9,
                    hovertemplate="<b>%{x}</b><br>Clientes Ativos: %{y:,.0f}<extra></extra>",
                )
            )

            auc_vals = pd.to_numeric(df_growth_auc["Net_Em_M"], errors="coerce").fillna(0.0)
            auc_diff = auc_vals.diff().fillna(0.0)
            auc_labels = [""] * int(len(auc_vals))
            if len(auc_vals) > 0:
                auc_labels[0] = f"R$ {auc_vals.iloc[0] / 1_000_000:.0f}M"
            if len(auc_vals) > 1:
                auc_labels[-1] = f"R$ {auc_vals.iloc[-1] / 1_000_000:.0f}M"

            # Não adiciona anotações para os valores de AUC
            auc_annotations = []

            fig_growth_auc.add_trace(
                go.Scatter(
                    x=df_growth_auc["ano_mes"],
                    y=df_growth_auc["Net_Em_M"],
                    name="AUC",
                    line=dict(color="#FFFFFF", width=2),
                    yaxis="y2",
                    mode="lines+markers",
                    hovertemplate="<b>%{x}</b><br>AUC: R$ %{y:,.2f}<extra></extra>",
                )
            )

            # Constantes para o layout dos cards
            PLOT_TOP = 0.84       # até onde vai o "gráfico" de verdade (0..1 em paper)
            CARDS_Y0 = 0.90       # início da faixa dos cards
            CARDS_Y1 = 0.995      # fim da faixa dos cards

            fig_growth_auc.update_layout(
                height=int(430 * TV_SCALE),
                margin=dict(l=20, r=140, t=15, b=15),
                annotations=auc_annotations,
                title=dict(
                    text="<b>CRESCIMENTO AUC E CLIENTES ATIVOS</b>",
                    font=dict(size=14, color="white"),
                    x=0.02,
                    y=0.885,  # posição ajustada para ficar abaixo dos cards
                    xanchor="left",
                    yanchor="top",
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showgrid=False,
                    showline=True,
                    linecolor="rgba(255, 255, 255, 0.2)",
                    tickfont=dict(color="white", size=10),
                    title=None,
                ),
                yaxis=dict(
                    title="Clientes Ativos",
                    title_font=dict(color="#948161"),
                    tickfont=dict(color="#948161"),
                    showgrid=True,
                    gridcolor="rgba(255, 255, 255, 0.1)",
                    gridwidth=0.5,
                    showline=True,
                    linecolor="rgba(255, 255, 255, 0.2)",
                    zeroline=False,
                    domain=[0, PLOT_TOP],  # define o domínio do eixo y
                ),
                yaxis2=dict(
                    title=None,
                    overlaying="y",
                    side="right",
                    automargin=True,
                    tickfont=dict(color="white", size=10),
                    showline=True,
                    linecolor="rgba(255, 255, 255, 0.2)",
                    gridcolor="rgba(255, 255, 255, 0.1)",
                    gridwidth=0.5,
                    tickmode="array",
                    tickvals=tick_vals,
                    ticktext=tick_text,
                    range=[nice_min, nice_max],
                    zeroline=False,
                    domain=[0, PLOT_TOP],  # define o domínio do eixo y2
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=0.845,  # posição ajustada para ficar na faixa livre
                    xanchor="center",
                    x=0.5,
                    font=dict(color="white", size=11),
                    bgcolor="rgba(0,0,0,0.2)",
                    bordercolor="rgba(255, 255, 255, 0.2)",
                ),
                hoverlabel=dict(
                    font_size=12,
                    font_family="Arial",
                    font_color="white",
                    bgcolor="rgba(32, 53, 47, 0.9)",
                    bordercolor="rgba(255, 255, 255, 0.2)",
                ),
            )

            st.plotly_chart(fig_growth_auc, use_container_width=True, config={"responsive": True})
        else:
            st.warning("Dados insuficientes para exibir o gráfico de Crescimento AUC e Clientes Ativos.")

    with col_upper_right:
        df_nps = carregar_dados_nps()
        # Aplicar filtro de data (junho a maio)
        df_nps, periodo_nps_label = filtrar_nps_a_partir_de_junho(df_nps)
        
        if not df_nps.empty:
            nps_color = "#ffffff"
            m_nps = _calcular_metricas_nps(df_nps)
            top3_df = _top3_assessores_por_aderencia(df_nps)

            if not top3_df.empty:
                medals = ["🥇", "🥈", "🥉"]
                row_divs = []
                for idx, row in enumerate(top3_df.itertuples(index=False), start=1):
                    cod = str(getattr(row, "ASSESSOR", "") or "")
                    nome = obter_nome_assessor(cod)
                    medal = medals[idx - 1] if idx <= len(medals) else ""
                    row_divs.append(
                        f"<div class='top3-v-item pos-{idx}'>"
                        f"<span class='top3-v-medal'>{medal} {idx}</span>"
                        f"<span class='top3-v-name'>{nome}</span>"
                        f"</div>"
                    )

                css_top3_nps = """
<style>
.top3-h-wrap { border: 1px solid rgba(46, 204, 113, 0.5) !important; border-radius: 10px !important; background: linear-gradient(180deg, rgba(46,204,113,0.12) 0%, rgba(46,204,113,0.04) 100%) !important; padding: 6px 8px 8px 8px !important; width: 90% !important; margin: 15px auto 6px auto !important; box-shadow: 0 1px 4px rgba(0,0,0,0.15) !important; }
.top3-h-title { text-align:center; font-weight:800; color:#fff; margin:0 0 3px 0 !important; letter-spacing:0.2px; font-size: 0.82em !important; line-height: 1.3 !important; }
.top3-v-list { display:flex; flex-direction:column; gap:2px !important; }
.top3-v-item { display:flex; align-items:center; justify-content:flex-start; padding:3px 8px !important; border-radius:6px !important; font-weight:700; color:#ffffff; font-size:0.78em !important; line-height: 1.4 !important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.top3-v-medal { width:40px; flex-shrink:0; text-align:left; }
.top3-v-name { flex:1; text-align:left; }
.top3-v-item.pos-1 { background: linear-gradient(135deg, rgba(255,213,79,.15), rgba(46,204,113,.03)); }
.top3-v-item.pos-2 { background: linear-gradient(135deg, rgba(207,216,220,.15), rgba(46,204,113,.03)); }
.top3-v-item.pos-3 { background: linear-gradient(135deg, rgba(255,171,145,.15), rgba(46,204,113,.03)); }
</style>
"""
                rows_html = "".join(row_divs)
                top3_block_html = css_top3_nps + f"""
<div class="top3-h-wrap">
<div class="top3-h-title">Top 3 — Aderência por Assessor - NPS</div>
<div class="top3-v-list">{rows_html}</div>
</div>
"""
            else:
                top3_block_html = "<div style='margin-top: 16px; text-align:center; color:#aaa; font-size:0.8em;'>Sem dados disponíveis para Top 3 de aderência.</div>"

            nps_html = f"""
<div class="dashboard-card nps-card">
<div class="nps-card-header" style="position: relative; margin-bottom: 4px;">
<h3 class="section-title" style="margin: 0; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 15px;">NPS — XP Aniversário</h3>
<div style="position: absolute; top: 0; right: 0; text-align: right;">
<div style="padding: 4px 8px; background: rgba(46, 204, 113, 0.15); border-radius: 12px; font-size: 0.75em; line-height: 1.2; display: block; color: #b8f7d4; width: fit-content; margin-left: auto; margin-bottom: 4px;">
<strong>Período = </strong> Junho 2025 - Junho 2026
</div>
</div>
</div>

<div class="nps-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin: 4px 0;">

<div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 2px 4px; text-align: center; display: flex; flex-direction: column; justify-content: center; min-height: 44px;">
<div style="font-size: 0.72em; opacity: 0.8; margin-bottom: 0px; color: #2ecc71; line-height: 1.1;">Total de Envios</div>
<div style="font-size: 1.1em; font-weight: 600; line-height: 1.0; margin-top: 0px;">{m_nps['total']}</div>
</div>

<div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 2px 4px; text-align: center; display: flex; flex-direction: column; justify-content: center; min-height: 44px;">
<div style="font-size: 0.72em; opacity: 0.8; margin-bottom: 0px; line-height: 1.1;">Total de Respostas</div>
<div style="font-size: 1.1em; font-weight: 600; line-height: 1.0; margin-top: 0px;">{m_nps['respondidos']}</div>
</div>

<div style="background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 2px 4px; text-align: center; display: flex; flex-direction: column; justify-content: center; min-height: 44px;">
<div style="font-size: 0.72em; opacity: 0.8; margin-bottom: 0px; line-height: 1.1;">Aderência</div>
<div style="font-size: 1.1em; font-weight: 600; line-height: 1.0; margin-top: 0px;">{_pct_br(m_nps['aderencia'])}</div>
</div>

<div style="background: rgba(46, 204, 113, 0.15); border-radius: 6px; padding: 2px 4px; text-align: center; display: flex; flex-direction: column; justify-content: center; min-height: 44px;">
<div style="font-size: 0.72em; opacity: 0.8; margin-bottom: 0px; line-height: 1.1;">NPS</div>
<div style="font-size: 1.1em; font-weight: 700; color: {nps_color}; line-height: 1.0; margin-top: 0px;">{_media_br(m_nps['nps'])}</div>
</div>

</div>

<div style="background: rgba(255, 255, 255, 0.05); border-radius: 4px; padding: 3px 6px; margin: 2px 0 6px; text-align: center; font-size: 0.7em;">
<div style="display: flex; justify-content: space-around; gap: 4px;">
<span style="color: #ff6b6b; white-space: nowrap;">Detratores: {m_nps['detratores']}</span>
<span style="color: #feca57; white-space: nowrap;">Neutros: {m_nps['neutros']}</span>
<span style="color: #1dd1a1; white-space: nowrap;">Promotores: {m_nps['promotores']}</span>
</div>
</div>

{top3_block_html}
</div>
"""
            st.markdown(nps_html, unsafe_allow_html=True)
        else:
            empty_html = """
<div class="dashboard-card nps-card" style="display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px;">
<h3 class="section-title" style="width: 100%; text-align: left; margin-bottom: 20px;">NPS — XP Aniversário</h3>
<div style="text-align: center; color: rgba(255, 255, 255, 0.5); font-size: 0.9em;">
<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5; margin-bottom: 12px;">
<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
</svg>
<div>Sem dados de NPS disponíveis</div>
</div>
</div>
"""
            st.markdown(dedent(empty_html), unsafe_allow_html=True)

    # =====================================================
    # SEÇÃO INFERIOR: MÉTRICAS (4 COLUNAS)
    # =====================================================
    df_objetivos = carregar_dados_objetivos()
    if df_objetivos is None or df_objetivos.empty:
        st.warning("Dados de objetivos não encontrados. Algumas métricas podem não ser exibidas.")
        df_objetivos = pd.DataFrame()

    mets = calcular_indicadores_objetivos(
        df_pos=df_pos_f,  # MTD para cálculos do mês
        df_obj=df_obj, 
        hoje=data_ref,
        df_pos_ytd=df_pos_full  # FULL para cálculos YTD
    )

    c1, c2, c3, c4 = st.columns(4)
    col1, col2, col3, col4 = c1, c2, c3, c4

    # --------------------------
    # COLUNA 1: CAPTAÇÃO MÊS
    # --------------------------
    with col1:
        st.markdown(
            """
            <div class="metric-card-kpi">
                <div style='text-align: center; margin: 0; padding: 4px 0;'>
                    <span style='color: white; font-weight: 900; font-size: 14px; line-height: 1.1; display: inline-block; letter-spacing: 0.3px;'>
                        CAPTAÇÃO LÍQUIDA MÊS
                    </span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='col-tv-inner'>", unsafe_allow_html=True)

        v_mes = float(mets.get("capliq_mes", {}).get("valor", 0.0) or 0.0)

        ano_atual = data_ref.year
        fallback_cap = 152_700_000.0 if ano_atual == 2025 else 0.0

        meta_anual = obter_meta_objetivo(ano_meta=ano_atual, coluna="cap_objetivo_ano", fallback=fallback_cap)
        v_ano = float(mets.get("capliq_ano", {}).get("valor", 0.0) or 0.0)

        mes_atual = data_ref.month
        obj_restante_ano = max(0.0, (meta_anual or 0.0) - v_ano)
        meses_restantes = max(1, 12 - mes_atual + 1)
        obj_total_mes = obj_restante_ano / meses_restantes

        data_atualizacao = pd.Timestamp(data_ref)
        primeiro_dia_mes = pd.Timestamp(data_atualizacao.year, data_atualizacao.month, 1)
        ultimo_dia_mes = pd.Timestamp(data_atualizacao.year, data_atualizacao.month, 1) + pd.offsets.MonthEnd(1)

        dias_uteis_mes = len(pd.bdate_range(start=primeiro_dia_mes, end=ultimo_dia_mes))
        dias_ate_atualizacao = len(pd.bdate_range(start=primeiro_dia_mes, end=data_atualizacao))

        threshold_teorico = (obj_total_mes * dias_ate_atualizacao) / dias_uteis_mes if dias_uteis_mes > 0 else 0
        threshold_teorico = min(threshold_teorico, obj_total_mes)
        threshold_mes = threshold_teorico

        st.markdown(
            f"""
            <div class='objetivo-card-topo'>
              <span>Objetivo Total:</span>
              <span class='valor'>{formatar_valor_curto(obj_total_mes)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_custom_progress_bars(objetivo_hoje_val=threshold_mes, realizado_val=v_mes, max_val=obj_total_mes, min_val=0)

        restante_mes = max(0.0, obj_total_mes - v_mes)
        dias_restantes = max(0, (ultimo_dia_mes - data_atualizacao).days)
        pct_realizado_total = v_mes / obj_total_mes * 100 if obj_total_mes > 0 else 0

        diferenca = v_mes - threshold_teorico
        pct_diferenca = (diferenca / threshold_teorico * 100) if threshold_teorico != 0 else 0
        
        if diferenca >= 0:
            diff_text = f"<span style='color:#2ecc7a'>{fmt_valor(diferenca)} ({pct_diferenca:+.1f}%) 🎯</span>"
            border_style = "border-left-color: #2ecc7a !important;"
        else:
            diff_text = f"<span style='color:#e74c3c'>{fmt_valor(diferenca)} ({pct_diferenca:+.1f}%)</span>"
            border_style = "border-left-color: #e74c3c !important;"

        val_restante = f"R$ {int(round(restante_mes / 1_000_000))}M" if restante_mes >= 1_000_000 else f"R$ {int(round(restante_mes / 1_000))}K"

        cards_mes_html = f"""
        <div class="tv-metric-grid">
          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px;">Dias Restantes</div>
            <div class="value" style="font-size: 0.9rem;">{dias_restantes}</div>
          </div>

          <div class="metric-pill metric-pill-top" style="{border_style} min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px;">Projetado vs Realizado</div>
            <div class="value" style="font-size: 0.8rem; line-height: 1.2;">{diff_text}</div>
          </div>

          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px; white-space: nowrap;">Percentual Realizado</div>
            <div class="value" style="font-size: 0.9rem; font-weight: bold;">{pct_realizado_total:.1f}%</div>
          </div>

          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px; white-space: nowrap;">Valor Restante</div>
            <div class="value" style="font-size: 0.9rem; font-weight: bold;"><span style="color:white">{val_restante}</span></div>
          </div>
        </div>
        """
        st.markdown(cards_mes_html, unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        items_mes, _ = top3_mes_cap(df_pos_mes_cap_top3, date_col="Data_Posicao", value_col="Captacao_Liquida_em_M", group_col="assessor_code")
        _render_top3_horizontal(items_mes, header_text="TOP 3 - Captação Mês")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------
    # COLUNA 2: CAPTAÇÃO ANO
    # --------------------------
    with col2:
        st.markdown(
            """
            <div class="metric-card-kpi">
                <div style='text-align: center; margin: 0; padding: 4px 0;'>
                    <span style='color: white; font-weight: 900; font-size: 14px; line-height: 1.1; display: inline-block; letter-spacing: 0.3px;'>
                        CAPTAÇÃO LÍQUIDA ANO
                    </span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='col-tv-inner'>", unsafe_allow_html=True)

        v_ano_col = float(mets.get("capliq_ano", {}).get("valor", 0.0) or 0.0)
        ano_atual_col = data_ref.year
        fallback_cap_col = 152_700_000.0 if ano_atual_col == 2025 else 0.0
        meta_eoy_col = obter_meta_objetivo(ano_meta=ano_atual_col, coluna="cap_objetivo_ano", fallback=fallback_cap_col)

        primeiro_dia_ano_col = pd.Timestamp(data_ref.year, 1, 1)
        ultimo_dia_ano_col = pd.Timestamp(data_ref.year, 12, 31)
        data_atualizacao_ano_col = pd.Timestamp(data_ref)
        total_dias_ano_col = (ultimo_dia_ano_col - primeiro_dia_ano_col).days + 1
        dias_ate_atualizacao_ano_col = (data_atualizacao_ano_col - primeiro_dia_ano_col).days + 1

        threshold_ano_col = (meta_eoy_col * dias_ate_atualizacao_ano_col) / total_dias_ano_col if total_dias_ano_col > 0 else 0.0
        threshold_ano_col = min(threshold_ano_col, float(meta_eoy_col or 0.0))

        st.markdown(
            f"""
            <div class='objetivo-card-topo'>
              <span>Objetivo Total:</span>
              <span class='valor'>{formatar_valor_curto(meta_eoy_col)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_custom_progress_bars(objetivo_hoje_val=threshold_ano_col, realizado_val=v_ano_col, max_val=float(meta_eoy_col or 0.01), min_val=0)

        restante_ano_col = max(0.0, float(meta_eoy_col or 0.0) - v_ano_col)
        dias_restantes_ano_col = max(0, (ultimo_dia_ano_col - data_atualizacao_ano_col).days)
        pct_realizado_ano_col = v_ano_col / meta_eoy_col * 100 if meta_eoy_col > 0 else 0

        diferenca_ano_col = v_ano_col - threshold_ano_col
        pct_diferenca_ano_col = (diferenca_ano_col / threshold_ano_col * 100) if threshold_ano_col != 0 else 0
        
        if diferenca_ano_col >= 0:
            diff_text_ano_col = f"<span style='color:#2ecc7a'>{fmt_valor(diferenca_ano_col)} ({pct_diferenca_ano_col:+.1f}%) 🎯</span>"
            border_style_ano_col = "border-left-color: #2ecc7a !important;"
        else:
            diff_text_ano_col = f"<span style='color:#e74c3c'>{fmt_valor(diferenca_ano_col)} ({pct_diferenca_ano_col:+.1f}%)</span>"
            border_style_ano_col = "border-left-color: #e74c3c !important;"

        val_restante_ano_col = f"R$ {int(round(restante_ano_col / 1_000_000))}M" if restante_ano_col >= 1_000_000 else f"R$ {int(round(restante_ano_col / 1_000))}K"

        cards_ano_html_col = f"""
        <div class="tv-metric-grid">
          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px;">Dias Restantes</div>
            <div class="value" style="font-size: 0.9rem;">{dias_restantes_ano_col}</div>
          </div>

          <div class="metric-pill metric-pill-top" style="{border_style_ano_col} min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px;">Projetado vs Realizado</div>
            <div class="value" style="font-size: 0.8rem; line-height: 1.2;">{diff_text_ano_col}</div>
          </div>

          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px; white-space: nowrap;">Percentual Realizado</div>
            <div class="value" style="font-size: 0.9rem; font-weight: bold;">{pct_realizado_ano_col:.1f}%</div>
          </div>

          <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
            <div class="label" style="font-size: 11px; white-space: nowrap;">Valor Restante</div>
            <div class="value" style="font-size: 0.9rem; font-weight: bold;"><span style="color:white">{val_restante_ano_col}</span></div>
          </div>
        </div>
        """
        st.markdown(cards_ano_html_col, unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        items_ano_col, _ = top3_ano_cap(df_pos_ano_cap_top3)
        _render_top3_horizontal(items_ano_col, header_text="Top 3 — Captação Ano")

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------
    # COLUNA 3: AUC - 2025
    # --------------------------
    with col3:
        st.markdown(
            """
            <div class="metric-card-kpi">
                <div style='text-align: center; margin: 0; padding: 4px 0;'>
                    <span style='color: white; font-weight: 900; font-size: 14px; line-height: 1.1; display: inline-block; letter-spacing: 0.3px;'>
                        AUC - 2025
                    </span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='col-tv-inner'>", unsafe_allow_html=True)

        try:
            hoje = pd.Timestamp(data_ref)
            ano_atual = hoje.year

            fallback_auc = 600_000_000.0 if ano_atual == 2025 else 0.0
            objetivo_ano_atual = obter_meta_objetivo(ano_meta=ano_atual, coluna="auc_objetivo_ano", fallback=fallback_auc)

            v_auc = arredondar_valor(float(mets.get("auc", {}).get("valor", 0.0) or 0.0), 2)

            primeiro_dia_ano_auc = pd.Timestamp(ano_atual, 1, 1)
            ultimo_dia_ano_auc = pd.Timestamp(ano_atual, 12, 31)
            total_dias_ano_auc = (ultimo_dia_ano_auc - primeiro_dia_ano_auc).days + 1
            dias_decorridos = (hoje - primeiro_dia_ano_auc).days + 1

            threshold_hoje = (objetivo_ano_atual * dias_decorridos) / total_dias_ano_auc if total_dias_ano_auc > 0 else 0.0
            threshold_hoje = min(threshold_hoje, float(objetivo_ano_atual or 0.0))

            dias_restantes_ano_auc = max(0, (ultimo_dia_ano_auc - hoje).days)
            diferenca = v_auc - threshold_hoje
            pct_diferenca = diferenca / threshold_hoje if threshold_hoje > 0 else 0
            pct_realizado = v_auc / objetivo_ano_atual * 100 if objetivo_ano_atual > 0 else 0
            restante_auc = max(0.0, float(objetivo_ano_atual or 0.0) - v_auc)

            st.markdown(
                f"""
                <div class='objetivo-card-topo'>
                  <span>Objetivo Total:</span>
                  <span class='valor'>{formatar_valor_curto(objetivo_ano_atual)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            render_custom_progress_bars(objetivo_hoje_val=threshold_hoje, realizado_val=v_auc, max_val=float(objetivo_ano_atual or 0.01), min_val=0)

            if diferenca >= 0:
                diff_text = f"<span style='color:#2ecc7a'>{fmt_valor(diferenca)} ({pct_diferenca:+.1f}%) 🎯</span>"
                border_style = "border-left-color: #2ecc7a !important;"
            else:
                diff_text = f"<span style='color:#e74c3c'>{fmt_valor(diferenca)} ({pct_diferenca:+.1f}%)</span>"
                border_style = "border-left-color: #e74c3c !important;"

            val_restante_auc = f"R$ {int(round(restante_auc / 1_000_000))}M" if restante_auc >= 1_000_000 else f"R$ {int(round(restante_auc / 1_000))}K"

            cards_auc_html = f"""
            <div class="tv-metric-grid">
              <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
                <div class="label" style="font-size: 11px;">Dias Restantes</div>
                <div class="value" style="font-size: 0.9rem;">{dias_restantes_ano_auc}</div>
              </div>

              <div class="metric-pill metric-pill-top" style="{border_style} min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
                <div class="label" style="font-size: 11px;">Projetado vs Realizado</div>
                <div class="value" style="font-size: 0.8rem; line-height: 1.2;">{diff_text}</div>
              </div>

              <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
                <div class="label" style="font-size: 11px; white-space: nowrap;">Percentual Realizado</div>
                <div class="value" style="font-size: 0.9rem; font-weight: bold;">{pct_realizado:.1f}%</div>
              </div>

              <div class="metric-pill metric-pill-top" style="min-height: 40px; display:flex; flex-direction:column; justify-content:center;">
                <div class="label" style="font-size: 11px; white-space: nowrap;">Valor Restante</div>
                <div class="value" style="font-size: 0.9rem; font-weight: bold;"><span style="color:white">{val_restante_auc}</span></div>
              </div>
            </div>
            """
            st.markdown(cards_auc_html, unsafe_allow_html=True)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            items_auc, _ = top3_mes_cap(df_pos_f, value_col="Net_Em_M")
            _render_top3_horizontal(items_auc, header_text="Top 3 — AUC")

        except Exception as e:
            st.error(f"Erro ao renderizar AUC: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------
    # COLUNA 4: Rumo a 1Bi
    # --------------------------
    with col4:
        st.markdown(
            """
            <div class="metric-card-kpi">
                <div style='text-align: center; margin: 0; padding: 4px 0;'>
                    <span style='color: white; font-weight: 900; font-size: 14px; line-height: 1.1; display: inline-block; letter-spacing: 0.3px;'>
                        RUMO A 1BI
                    </span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='col-tv-inner'>", unsafe_allow_html=True)

        render_rumo_a_1bi(auc_base_inicial_2025=AUC_BASE_2025)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Close dashboard wrapper
    st.markdown("</div>", unsafe_allow_html=True)

    # CSS de override para controle de escala
    st.markdown(
        f"""
    <style>
    /* ==========================
       SCALE PATCH (proporcional)
       ========================== */
    :root {{
      --tv-scale: {TV_SCALE} !important; /* domina o valor final */
    }}

    /* Cards principais (o que você mais sente "não diminuir") */
    .dashboard-card {{
      border-radius: calc(14px * var(--tv-scale)) !important;
      padding: calc(14px * var(--tv-scale)) calc(16px * var(--tv-scale)) !important;
      margin-bottom: calc(14px * var(--tv-scale)) !important;
      font-size: calc(0.95em * var(--tv-scale)) !important;
    }}

    .metric-card-kpi {{
      border-radius: calc(12px * var(--tv-scale)) !important;
      padding: calc(4px * var(--tv-scale)) calc(8px * var(--tv-scale)) !important;
      margin: calc(2px * var(--tv-scale)) !important;
      font-size: calc(0.90em * var(--tv-scale)) !important;
    }}

    /* Esses eram os "vilões" por estarem fixos em 440px */
    .dashboard-card.nps-card,
    .stPlotlyChart {{
      height: calc(440px * var(--tv-scale)) !important;
      min-height: calc(440px * var(--tv-scale)) !important;
      max-height: calc(440px * var(--tv-scale)) !important;
    }}

    /* Grid dos mini-cards (tava fixo em 120px) */
    .tv-metric-grid {{
      height: calc(120px * var(--tv-scale)) !important;
      min-height: calc(120px * var(--tv-scale)) !important;
    }}

    /* Corrige tamanhos inline dentro dos mini-cards (você usa min-height/font-size no HTML) */
    .metric-pill-top {{
      min-height: calc(40px * var(--tv-scale)) !important;
    }}
    .metric-pill-top .label {{
      font-size: calc(11px * var(--tv-scale)) !important;
    }}
    .metric-pill-top .value {{
      font-size: calc(0.90rem * var(--tv-scale)) !important;
    }}

    /* Tabela (padding/altura eram fixos e "seguravam" o tamanho) */
    .ranking-table thead tr:first-child th {{
      padding: calc(12px * var(--tv-scale)) calc(10px * var(--tv-scale)) !important;
    }}
    .ranking-table thead tr:nth-child(2) th {{
      padding: calc(10px * var(--tv-scale)) calc(8px * var(--tv-scale)) !important;
    }}
    .ranking-table tbody td {{
      padding: calc(10px * var(--tv-scale)) calc(12px * var(--tv-scale)) !important;
      height: calc(42px * var(--tv-scale)) !important;
    }}

    /* Espaçamento geral */
    .dbv-dashboard-root {{
      gap: calc(18px * var(--tv-scale)) !important;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

#1223
