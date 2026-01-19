# Dash_Salão_Atualizado.py

import re
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import date
import numpy as np
import unicodedata
from textwrap import dedent

def st_html(html: str):
    """Helper function to clean HTML before rendering with st.markdown"""
    html = dedent(html).strip()
    # Remove blank lines that would break markdown's HTML block
    html = re.sub(r"\n[ \t]*\n+", "\n", html)
    st.markdown(html, unsafe_allow_html=True)


# =========================
# MAPEAMENTO DE ASSESSORES
# =========================
ASSESSORES_MAP = {
    "A92300": "Adil Amorim",
    "A95715": "André Norat",
    "A87867": "Arthur Linhares",
    "A95796": "Artur Vaz",
    "A96676": "Artur Vaz",
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
    "A41471": "João Georg de Andrade",
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
    "A52794": "Luiz Mesquita",
    "D00005": "Rhana Pitta",
    "A94665": "Mesa Comercial",
    "D00015": "Breno Freire"
}

def obter_nome_assessor(codigo: str) -> str:
    """Converte código (ex: A12345 ou 12345) para Nome."""
    if not codigo:
        return "-"
    codigo_str = str(codigo).strip()
    
    # Mapeamento específico para Artur Vaz - usar apenas o código A95796
    if codigo_str == "A96676":
        return "-"  # Ignorar este código para evitar dupla contagem
    if codigo_str == "A95796":
        return "Artur Vaz"

    # 1. Tenta exato
    if codigo_str in ASSESSORES_MAP:
        return ASSESSORES_MAP[codigo_str]

    # 2. Tenta adicionar 'A'
    if codigo_str.isdigit():
        codigo_com_a = f"A{codigo_str}"
        if codigo_com_a in ASSESSORES_MAP:
            return ASSESSORES_MAP[codigo_com_a]

    # 3. Tenta remover 'A'
    if codigo_str.startswith("A") and codigo_str[1:].isdigit():
        if codigo_str in ASSESSORES_MAP:
            return ASSESSORES_MAP[codigo_str]

    return codigo_str

def _primeiro_nome_sobrenome(nome_completo: str) -> str:
    """Formata para 'Nome Sobrenome'."""
    if not nome_completo:
        return ""
    tokens = re.split(r"\s+", str(nome_completo).strip())
    if not tokens:
        return ""
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


# =========================
# CONTROLE DE ESCALA
# =========================
TV_SCALE = 0.88  # ajuste fino (0.85~0.88 se quiser menos redução)


# =========================
# CONFIG DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard DBV Capital",
    page_icon="📊",
    layout="wide",
)

def _norm_txt(x: object) -> str:
    s = "" if x is None else str(x)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.strip().lower()

def _parse_datas_robusto(serie):
    import re
    s = pd.Series(serie).copy()

    def _parse_one(x):
        t = ("" if x is None else str(x)).strip()
        if t == "" or t.lower() in ("nat", "nan", "none", "-"):
            return pd.NaT

        # serial Excel
        try:
            test = t.replace(".", "", 1).replace("-", "", 1)
            if test.isdigit():
                v = float(t)
                if 1 <= v <= 60000:
                    return pd.to_datetime(v, origin="1899-12-30", unit="D", errors="coerce")
        except Exception:
            pass

        # ISO estrito
        if re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}$", t):
            return pd.to_datetime(t.replace("/", "-"), format="%Y-%m-%d", errors="coerce")

        # MM/YYYY
        mmyyyy = re.match(r"^(\d{1,2})/(\d{4})$", t)
        if mmyyyy:
            m, y = int(mmyyyy.group(1)), int(mmyyyy.group(2))
            if 1 <= m <= 12:
                return pd.to_datetime(f"{y:04d}-{m:02d}-01", format="%Y-%m-%d", errors="coerce")

        # BR
        if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", t) or re.match(r"^\d{1,2}-\d{1,2}-\d{4}$", t):
            return pd.to_datetime(t, dayfirst=True, errors="coerce")

        return pd.to_datetime(t, errors="coerce")

    dt = s.apply(_parse_one)
    dt = pd.to_datetime(dt, errors="coerce")
    try:
        dt = dt.dt.tz_localize(None).dt.normalize()
    except Exception:
        pass
    return dt

def formatar_moeda(valor: float) -> str:
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


# =========================
# CARREGAMENTO DO BANCO (ÚNICO)
# =========================
@st.cache_data(show_spinner=False)
def carregar_dados_produtos():
    caminho_db = Path(__file__).parent.parent / "DBV Capital_Produtos.db"
    if not caminho_db.exists():
        st.error(f"Arquivo do banco de dados não encontrado em: {caminho_db}")
        return pd.DataFrame(), "N/A"

    conn = sqlite3.connect(str(caminho_db))
    try:
        # Verificar tabelas disponíveis
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [t[0] for t in cursor.fetchall()]
        
        # Tentar encontrar a tabela correta
        nome_tabela = next((t for t in tabelas if 'produtos' in t.lower() or 'planilha' in t.lower()), None)
        
        if not nome_tabela:
            st.error("Nenhuma tabela de produtos encontrada no banco de dados.")
            return pd.DataFrame(), "N/A"
            
        # Obter as colunas da tabela
        cursor.execute(f"PRAGMA table_info(\"{nome_tabela}\")")
        colunas = [col[1] for col in cursor.fetchall()]
        
        # Mapear colunas conhecidas com base nos nomes exatos fornecidos
        mapeamento_colunas = {}
        
        # Mapear data
        if 'Data' in colunas:
            mapeamento_colunas['Data'] = 'data'
        
        # Mapear valor_negocio
        if 'Valor Negócio (R$)' in colunas:
            mapeamento_colunas['Valor Negócio (R$)'] = 'valor_negocio'
        
        # Mapear linha_receita
        if 'Linha Receita' in colunas:
            mapeamento_colunas['Linha Receita'] = 'linha_receita'
        
        # Mapear codigo_assessor
        if 'Código Assessor' in colunas:
            mapeamento_colunas['Código Assessor'] = 'codigo_assessor'
        
        # Se alguma coluna não foi encontrada, tentar encontrar por similaridade
        if len(mapeamento_colunas) < 4:
            for c in colunas:
                c_lower = c.lower()
                if 'data' in c_lower and 'data' not in [v.lower() for v in mapeamento_colunas.values()]:
                    mapeamento_colunas[c] = 'data'
                elif any(termo in c_lower for termo in ['valor', 'negocio', 'negócio']) and 'valor_negocio' not in [v.lower() for v in mapeamento_colunas.values()]:
                    mapeamento_colunas[c] = 'valor_negocio'
                elif 'linha receita' in c_lower and 'linha_receita' not in [v.lower() for v in mapeamento_colunas.values()]:
                    mapeamento_colunas[c] = 'linha_receita'
                elif 'código assessor' in c_lower and 'codigo_assessor' not in [v.lower() for v in mapeamento_colunas.values()]:
                    mapeamento_colunas[c] = 'codigo_assessor'
        
        # Se ainda faltarem colunas, tentar encontrar por similaridade mais ampla
        if len(mapeamento_colunas) < 4:
            for c in colunas:
                c_lower = c.lower()
                if 'data' not in [v.lower() for v in mapeamento_colunas.values()] and ('data' in c_lower or 'dt' in c_lower):
                    mapeamento_colunas[c] = 'data'
                elif 'valor_negocio' not in [v.lower() for v in mapeamento_colunas.values()] and ('valor' in c_lower or 'venda' in c_lower):
                    mapeamento_colunas[c] = 'valor_negocio'
                elif 'linha_receita' not in [v.lower() for v in mapeamento_colunas.values()] and ('linha' in c_lower or 'receita' in c_lower or 'categoria' in c_lower):
                    mapeamento_colunas[c] = 'linha_receita'
                elif 'codigo_assessor' not in [v.lower() for v in mapeamento_colunas.values()] and ('cod' in c_lower or 'assessor' in c_lower):
                    mapeamento_colunas[c] = 'codigo_assessor'
        
        # Verificar se encontramos todas as colunas necessárias
        colunas_necessarias = {'data', 'valor_negocio', 'linha_receita', 'codigo_assessor'}
        colunas_encontradas = set(v.lower() for v in mapeamento_colunas.values())
        
        if not colunas_necessarias.issubset(colunas_encontradas):
            st.error(f"Não foi possível mapear todas as colunas necessárias. Colunas encontradas: {colunas}")
            st.error(f"Colunas mapeadas: {mapeamento_colunas}")
            return pd.DataFrame(), "N/A"
        
        # Construir a consulta SQL com as colunas mapeadas
        sql_cols = ', '.join(f'"{c}" as "{v}"' for c, v in mapeamento_colunas.items())
        query = f'SELECT {sql_cols} FROM "{nome_tabela}"'
        
        # Carregar os dados com as colunas renomeadas
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados: {str(e)}")
        return pd.DataFrame(), "N/A"
    finally:
        conn.close()

    if df.empty:
        return df, "N/A"

    # Verificar se todas as colunas necessárias estão presentes
    colunas_necessarias = {'data', 'valor_negocio', 'codigo_assessor', 'linha_receita'}
    colunas_faltando = colunas_necessarias - set(df.columns)
    
    if colunas_faltando:
        st.warning(f"Aviso: As seguintes colunas não foram encontradas e serão criadas vazias: {', '.join(colunas_faltando)}")
        for col in colunas_faltando:
            df[col] = '' if col == 'linha_receita' else (0.0 if col == 'valor_negocio' else pd.NaT)

    if "data" in df.columns:
        df["data"] = _parse_datas_robusto(df["data"])
        df = df.dropna(subset=["data"]).reset_index(drop=True)
    else:
        df["data"] = pd.NaT

    if "valor_negocio" in df.columns:
        df["valor_negocio"] = df["valor_negocio"].astype(str).str.replace(r"[^\d.-]", "", regex=True)
        df["valor_negocio"] = pd.to_numeric(df["valor_negocio"], errors="coerce").fillna(0.0)
    else:
        df["valor_negocio"] = 0.0
        st.warning("Coluna 'valor_negocio' não encontrada. Usando valor padrão 0.0")

    if "linha_receita" not in df.columns:
        df["linha_receita"] = ""

    if "codigo_assessor" not in df.columns:
        if "assessor" in df.columns:
            df["codigo_assessor"] = df["assessor"]
        else:
            df["codigo_assessor"] = ""

    data_mais_recente = (
        df["data"].max().strftime("%d/%m/%Y")
        if not df.empty and "data" in df.columns and not df["data"].empty
        else "N/A"
    )
    return df, data_mais_recente


# =========================
# PÁGINA
# =========================
df, data_atualizacao = carregar_dados_produtos()

css = f"""
<div style='text-align: center; margin: 0 auto 2px auto;'>
    <span style='font-size: calc(0.8rem * var(--tv-scale)); color: #FFFFFF; font-weight: 400;'>
        Atualizado em: {data_atualizacao}
    </span>
</div>

<style>
[data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
    margin-top: 0 !important;
    background: #211c5a !important;
}}

section[data-testid="stSidebar"],
header[data-testid="stHeader"] {{
    display: none !important;
}}

.block-container {{
    padding: calc(0.8rem * var(--tv-scale)) calc(1% * var(--tv-scale)) !important;
    max-width: 100% !important;
}}

:root {{
    --tv-scale: {TV_SCALE};
    --radius: calc(14px * var(--tv-scale));
    --bg-primary: #211c5a;
    --top3-gold: linear-gradient(135deg, rgba(255,215,0,0.18) 0%, rgba(58,163,255,0.10) 65%, rgba(0,0,0,0.00) 100%);
    --top3-silver: linear-gradient(135deg, rgba(192,192,192,0.18) 0%, rgba(58,163,255,0.10) 65%, rgba(0,0,0,0.00) 100%);
    --top3-bronze: linear-gradient(135deg, rgba(205,127,50,0.18) 0%, rgba(58,163,255,0.10) 65%, rgba(0,0,0,0.00) 100%);
    --accent: #3AA3FF;
    --accent-2: #1857DC;
    --card-gradient: linear-gradient(
        145deg,
        rgba(58, 163, 255, 0.22) 0%,
        rgba(24, 87, 220, 0.12) 55%,
        rgba(0, 0, 0, 0.12) 100%
    ) !important;
    --mini-gradient: linear-gradient(
        145deg,
        rgba(58, 163, 255, 0.38) 0%,
        rgba(24, 87, 220, 0.18) 70%
    );
    --text-primary: #ffffff;
    --line: rgba(255,255,255,0.10);
    --muted: rgba(255,255,255,0.75);
    --shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
}}

.dashboard-card {{
    background: var(--card-gradient) !important;
    border-radius: var(--radius) !important;
    padding: calc(6px * var(--tv-scale)) calc(8px * var(--tv-scale)) !important;
    box-shadow: var(--shadow) !important;
    color: var(--text-primary) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;

    height: calc(380px * var(--tv-scale)) !important;
    min-height: calc(380px * var(--tv-scale)) !important;

    box-sizing: border-box !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
}}

.section-title {{
    color: var(--text-primary) !important;
    font-size: calc(1.3rem * var(--tv-scale)) !important; /* Aumentado de 1.02rem para 1.3rem */
    font-weight: 900 !important;
    margin: 0 0 calc(5px * var(--tv-scale)) 0 !important;
    padding-bottom: calc(5px * var(--tv-scale)) !important;
    border-bottom: 1px solid var(--line) !important;
    text-align: center !important;
    letter-spacing: 0.5px;
}}

.card-body {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: calc(4px * var(--tv-scale));
    flex: 1;
    min-height: 0;
}}

.period-box {{
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: calc(10px * var(--tv-scale));
    padding: calc(3px * var(--tv-scale));
    padding-bottom: calc(4px * var(--tv-scale)); /* ↓ respiro, para sobrar p/ conteúdo */
    background: rgba(255,255,255,0.04);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
}}

.period-header {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: calc(10px * var(--tv-scale));
    margin-bottom: calc(3px * var(--tv-scale));
}}

.period-title {{
    font-weight: 900;
    font-size: calc(0.92rem * var(--tv-scale)); /* ↑ um pouco */
    color: #fff;
    text-align: center;
    line-height: 1.05;
}}

.metric-block {{
    display: flex;
    flex-direction: column;
    gap: calc(2px * var(--tv-scale));
    margin-bottom: calc(4px * var(--tv-scale));

    flex: 1;        /* <<< chave: cada bloco ocupa “metade” e evita área morta */
    min-height: 0;  /* <<< chave p/ não estourar */
}}

.metric-block:last-child {{
    margin-bottom: 0;
}}

.metric-block + .metric-block {{
    margin-top: calc(10px * var(--tv-scale));
    padding-top: calc(8px * var(--tv-scale));
    border-top: 1px solid rgba(255,255,255,0.25);
}}

.mini-kpi-card{{
    position: relative;
    overflow: hidden;
    border-radius: calc(10px * var(--tv-scale));
    padding: calc(3px * var(--tv-scale)) calc(6px * var(--tv-scale));
    background: transparent; /* agora o fundo base vem do ::after */
    border: 1px solid rgba(58,163,255,0.35);
    box-shadow: 0 2px 10px rgba(0,0,0,0.10);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

/* Glow "vivo" por trás (efeito premium) */
.mini-kpi-card::before{{
    content:"";
    position:absolute;
    inset: calc(-18px * var(--tv-scale));
    border-radius: inherit;
    background: conic-gradient(
        from 180deg,
        rgba(58,163,255,0.00),
        rgba(58,163,255,0.70),
        rgba(24,87,220,0.60),
        rgba(58,163,255,0.00)
    );
    filter: blur(calc(14px * var(--tv-scale)));
    opacity: 0.45;
    animation: kpiGlowSpin 7s linear infinite;
    pointer-events: none;
}}

/* Fundo real do card + leve "vidro" por cima */
.mini-kpi-card::after{{
    content:"";
    position:absolute;
    inset: 0;
    border-radius: inherit;
    background: var(--mini-gradient);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.18),
        inset 0 -1px 0 rgba(0,0,0,0.12);
    pointer-events: none;
}}

/* Garante que os textos fiquem acima dos pseudo-elementos */
.mini-kpi-card > *{{
    position: relative;
    z-index: 1;
}}

/* Efeito hover para desktop */
@media (hover: hover) and (pointer: fine) {{
    .mini-kpi-card:hover{{
        transform: translateY(calc(-1px * var(--tv-scale)));
        box-shadow: 0 8px 18px rgba(0,0,0,0.18);
    }}
}}

/* Animação do glow */
@keyframes kpiGlowSpin{{
    0%   {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Se o dispositivo pedir menos animação, respeita */
@media (prefers-reduced-motion: reduce){{
    .mini-kpi-card::before{{ animation: none; }}
}}

.mini-kpi-label {{
    font-size: calc(0.82rem * var(--tv-scale)); /* ↑ */
    color: rgba(255,255,255,0.86);
    font-weight: 800;
    text-align: center;
    width: 100%;
    line-height: 1.05;
}}

.mini-kpi-value {{
    margin-top: calc(2px * var(--tv-scale));
    font-size: calc(1.05rem * var(--tv-scale)); /* ↑ */
    font-weight: 950;
    color: #fff;
    white-space: nowrap;
    text-align: center;
    width: 100%;
    line-height: 1.05;
}}

.top3 {{
    /* <<< chave: faz o Top 3 “crescer” e ocupar o espaço sobrando */
    flex: 1;
    min-height: 0;

    display: flex;
    flex-direction: column;

    /* distribui o espaço extra entre título + 3 itens, reduzindo o “vazio no final” */
    justify-content: space-between;

    gap: calc(2px * var(--tv-scale));
    margin-top: calc(3px * var(--tv-scale));
    padding: calc(2px * var(--tv-scale)) 0;
}}

.top3-title {{
    font-size: calc(0.78rem * var(--tv-scale)); /* ↑ */
    color: rgba(255,255,255,0.78);
    font-weight: 800;
    margin: 0;
    line-height: 1.05;
    text-align: center !important; /* Centraliza o título */
}}

.top3-item {{
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: calc(10px * var(--tv-scale));

    font-size: calc(0.78rem * var(--tv-scale));
    font-weight: 700;
    color: #fff;

    height: calc(26px * var(--tv-scale));
    padding: 0 calc(8px * var(--tv-scale));
    line-height: 1.05;

    border-radius: calc(10px * var(--tv-scale));
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.035);
    box-sizing: border-box;
}}

/* Camada de gradiente por cima do fundo base */
.top3-item::before{{
    content:"";
    position:absolute;
    inset:0;
    border-radius: inherit;
    opacity: 0.85;
    pointer-events:none;
}}

/* Aplica gradiente por ordem (1º, 2º, 3º) */
.top3-item:nth-child(2)::before{{ background: var(--top3-gold); }}
.top3-item:nth-child(3)::before{{ background: var(--top3-silver); }}
.top3-item:nth-child(4)::before{{ background: var(--top3-bronze); }}

/* Garante que o texto fique acima */
.top3-item > *{{
    position: relative;
    z-index: 1;
}}

.top3-item > span:first-child {{
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
</style>
"""

st.markdown(css, unsafe_allow_html=True)


# =========================
# LÓGICA DE NEGÓCIO E FILTROS
# =========================
def _pick_cols(df_: pd.DataFrame):
    area_col = "linha_receita"
    ass_col = "codigo_assessor" if "codigo_assessor" in df_.columns else ("assessor" if "assessor" in df_.columns else None)
    return area_col, ass_col

def _filter_area(df_: pd.DataFrame, area_values: list[str], card_title: str = None) -> pd.DataFrame:
    if df_.empty:
        return df_
    area_col, _ = _pick_cols(df_)
    if area_col not in df_.columns:
        return df_.iloc[0:0].copy()

    targets = {_norm_txt(v) for v in area_values}
    s = df_[area_col].astype(str).apply(_norm_txt)
    filtered = df_[s.isin(targets)].copy()

    # Removido o filtro que excluía "Câmbio Merc. Inter." conforme solicitado
    # Agora todos os produtos de câmbio serão incluídos nos cálculos

    return filtered

def _period_month(df_area: pd.DataFrame):
    if df_area.empty or df_area["data"].dropna().empty:
        return None, None, "Mês", False

    last_dt = df_area["data"].max()
    per = last_dt.to_period("M")
    di = date(per.year, per.month, 1)
    df_ = last_dt.date()
    
    # Dicionário com os nomes dos meses em português
    month_names_pt = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    # Formata como "Mmm/YYYY" (ex: "Dez/2025")
    month_year = f"{month_names_pt[per.month]}/{per.year}"

    info_flag = (per.year != date.today().year) or (per.month != date.today().month)
    return di, df_, month_year, info_flag

def _period_year(df_area: pd.DataFrame):
    if df_area.empty or df_area["data"].dropna().empty:
        return None, None, "Ano", False

    today = date.today()
    di = date(today.year, 1, 1)
    df_ = today

    mask = (df_area["data"].dt.date >= di) & (df_area["data"].dt.date <= df_)
    if mask.any():
        return di, df_, "Ano", False

    last_dt = df_area["data"].max()
    y = int(last_dt.year)
    di2 = date(y, 1, 1)
    df2 = date(y, 12, 31)
    return di2, df2, "Ano", True

def _calc_block(df_area: pd.DataFrame, di: date, df_: date):
    if df_area.empty or di is None or df_ is None:
        return 0.0, 0, [], []

    _, ass_col = _pick_cols(df_area)
    mask = (df_area["data"].dt.date >= di) & (df_area["data"].dt.date <= df_)
    d = df_area.loc[mask].copy()
    if d.empty:
        return 0.0, 0, [], []

    valor_total = float(d["valor_negocio"].sum())
    qtd_total = int(d.shape[0])

    if ass_col is None:
        return valor_total, qtd_total, [], []

    d[ass_col] = d[ass_col].astype(str).str.strip()
    d.loc[d[ass_col].isin(["", "nan", "None"]), ass_col] = "N/A"

    d = d[~d[ass_col].astype(str).str.upper().isin(["DBV999", "A94665", "MESA COMERCIAL", "A72084"])]
    d["nome_assessor_mapeado"] = d[ass_col].apply(obter_nome_assessor)

    nomes_invalidos = ["-", "", "NAN", "NONE", "VAZIO", "N/A"]
    d = d[~d["nome_assessor_mapeado"].astype(str).str.upper().isin(nomes_invalidos)]
    
    # Remover Cesar Lima do ranking
    d = d[~d["nome_assessor_mapeado"].str.contains("Cesar Lima", case=False, na=False)]

    top_val = (
        d.groupby("nome_assessor_mapeado")["valor_negocio"].sum()
        .sort_values(ascending=False).head(3).reset_index()
    )

    top_qtd = (
        d.groupby("nome_assessor_mapeado").size()
        .sort_values(ascending=False).head(3).reset_index(name="qtd")
    )

    top3_valor = [(str(r["nome_assessor_mapeado"]), float(r["valor_negocio"])) for _, r in top_val.iterrows()]
    top3_qtd = [(str(r["nome_assessor_mapeado"]), int(r["qtd"])) for _, r in top_qtd.iterrows()]
    return valor_total, qtd_total, top3_valor, top3_qtd

def _render_top3_valor(top3):
    rows = ["<div class='top3-title'>Top 3 Assessores</div>"]
    medals = ["🥇", "🥈", "🥉"]
    for i in range(3):
        display_name = ""
        medal_icon = medals[i]
        if i < len(top3):
            nome_completo, _ = top3[i]
            display_name = _primeiro_nome_sobrenome(nome_completo)

        rows.append(
            f"<div class='top3-item'>"
            f"<span><span style='font-size: 1.15em;'>{medal_icon}</span> {display_name}</span>"
            f"<span></span>"
            f"</div>"
        )
    return "".join(rows)

def _render_top3_qtd(top3):
    rows = ["<div class='top3-title'>Top 3 Assessores</div>"]
    medals = ["🥇", "🥈", "🥉"]
    for i in range(3):
        display_name = ""
        medal_icon = medals[i]
        if i < len(top3):
            nome_completo, _ = top3[i]
            display_name = _primeiro_nome_sobrenome(nome_completo)

        rows.append(
            f"<div class='top3-item'>"
            f"<span><span style='font-size: 1.15em;'>{medal_icon}</span> {display_name}</span>"
            f"<span></span>"
            f"</div>"
        )
    return "".join(rows)

def render_area_card(card_title: str, df_all: pd.DataFrame, area_values: list[str]):
    df_area = _filter_area(df_all, area_values, card_title)
    
    # Verificar se há dados para esta área
    if df_area.empty or df_area["data"].dropna().empty:
        # Exibir card vazio se não houver dados
        html = f"""
        <div class="dashboard-card">
            <h3 class="section-title">{card_title}</h3>
            <div class="card-body">
                <div class="period-box">
                    <div class="period-header">
                        <div class="period-title">Sem Dados</div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Valor de Negócio</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Qtd Negócios</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                </div>
                <div class="period-box">
                    <div class="period-header">
                        <div class="period-title">Sem Dados</div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Valor de Negócio</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Qtd Negócios</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        st_html(html)
        return
    
    # Obter a data mais recente dos dados desta área
    data_mais_recente_area = df_area["data"].max()
    
    # Converter data_atualizacao para datetime para comparação
    dados_desatualizados = False
    try:
        if data_atualizacao != "N/A":
            data_atualizacao_dt = pd.to_datetime(data_atualizacao, format="%d/%m/%Y")
            
            # Se os dados da área forem anteriores à data de atualização, marcar como desatualizados
            if data_mais_recente_area < data_atualizacao_dt:
                dados_desatualizados = True
    except Exception:
        # Se houver erro na conversão, continua com a exibição normal
        pass

    # Se os dados estiverem desatualizados, exibir card vazio
    if dados_desatualizados:
        html = f"""
        <div class="dashboard-card">
            <h3 class="section-title">{card_title}</h3>
            <div class="card-body">
                <div class="period-box">
                    <div class="period-header">
                        <div class="period-title">-</div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Valor de Negócio</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Qtd Negócios</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                </div>
                <div class="period-box">
                    <div class="period-header">
                        <div class="period-title">-</div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Valor de Negócio</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                    <div class="metric-block">
                        <div class="mini-kpi-card">
                            <div class="mini-kpi-label">Qtd Negócios</div>
                            <div class="mini-kpi-value">-</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        st_html(html)
        return

    di_m, df_m, lab_m, _ = _period_month(df_area)
    di_y, df_y, lab_y, _ = _period_year(df_area)

    v_m, q_m, topv_m, topq_m = _calc_block(df_area, di_m, df_m)
    v_y, q_y, topv_y, topq_y = _calc_block(df_area, di_y, df_y)

    html = f"""
    <div class="dashboard-card">
        <h3 class="section-title">{card_title}</h3>

        <div class="card-body">
            <div class="period-box">
                <div class="period-header">
                    <div class="period-title">{lab_m}</div>
                </div>

                <div class="metric-block">
                    <div class="mini-kpi-card">
                        <div class="mini-kpi-label">{"Prêmio Mensal" if card_title in ["Vida", "Auto/RE"] else "Valor de Negócio"}</div>
                        <div class="mini-kpi-value">{formatar_moeda(v_m)}</div>
                    </div>
                    <div class="top3">{_render_top3_valor(topv_m)}</div>
                </div>

                <div class="metric-block">
                    <div class="mini-kpi-card">
                        <div class="mini-kpi-label">Qtd Negócios</div>
                        <div class="mini-kpi-value">{q_m}</div>
                    </div>
                    <div class="top3">{_render_top3_qtd(topq_m)}</div>
                </div>
            </div>

            <div class="period-box">
                <div class="period-header">
                    <div class="period-title">{lab_y}</div>
                </div>

                <div class="metric-block">
                    <div class="mini-kpi-card">
                        <div class="mini-kpi-label">{"Prêmio Anual" if card_title in ["Vida", "Auto/RE"] else "Valor de Negócio"}</div>
                        <div class="mini-kpi-value">{formatar_moeda(v_y)}</div>
                    </div>
                    <div class="top3">{_render_top3_valor(topv_y)}</div>
                </div>

                <div class="metric-block">
                    <div class="mini-kpi-card">
                        <div class="mini-kpi-label">Qtd Negócios</div>
                        <div class="mini-kpi-value">{q_y}</div>
                    </div>
                    <div class="top3">{_render_top3_qtd(topq_y)}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st_html(html)


if df.empty:
    st.error("Não encontrei dados no banco DBV Capital_Produtos.db (tabelas 'produtos' / 'DBV Capital_Produtos_Planilha1')")
    st.stop()

AREA_MAP = {
    "Vida": ["Vida", "Seguros", "Seguro", "Vida/Seguros", "Vida e Seguros"],
    "Auto/RE": ["Auto/RE", "AutoRE", "Auto", "RE"],
    "Saúde": ["Saúde", "Saude"],
    "Câmbio": ["Câmbio", "Cambio"],
    "Consórcio": ["Consórcio", "Consorcio"],
    "Crédito": ["Crédito", "Credito"],
}

# GRID 2 x 3
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    render_area_card("Vida", df, AREA_MAP["Vida"])
with row1_col2:
    render_area_card("Auto/RE", df, AREA_MAP["Auto/RE"])
with row1_col3:
    render_area_card("Saúde", df, AREA_MAP["Saúde"])

st.markdown("<div style='height: calc(4px * var(--tv-scale));'></div>", unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    render_area_card("Câmbio", df, AREA_MAP["Câmbio"])
with row2_col2:
    render_area_card("Consórcio", df, AREA_MAP["Consórcio"])
with row2_col3:
    render_area_card("Crédito", df, AREA_MAP["Crédito"])

st.markdown("<div style='height: calc(8px * var(--tv-scale));'></div>", unsafe_allow_html=True)
