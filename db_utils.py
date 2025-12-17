# db_utils.py
# Utilitários de conexão e leitura dos bancos SQLite da DBV Capital

from pathlib import Path
from functools import lru_cache
from typing import Optional

import pandas as pd
import sqlite3


# =============================================================================
# BASES DE CAMINHO
# =============================================================================

# Pasta raiz do projeto: onde este arquivo db_utils.py está salvo
BASE_DIR = Path(__file__).resolve().parent

# Subpastas relevantes
PAGES_DIR = BASE_DIR / "pages"
DATA_DIR = BASE_DIR / "data"
CSV_EXPORT_DIR = BASE_DIR / "csv_export"


# =============================================================================
# LOCALIZAÇÃO DOS ARQUIVOS .DB
# =============================================================================

def _find_file(filename: str) -> Path:
    """
    Procura o arquivo em algumas pastas padrão do projeto, na seguinte ordem:
    1. pages/
    2. data/
    3. raiz do projeto

    Retorna um Path absoluto se encontrar, senão gera FileNotFoundError.
    """
    search_dirs = [PAGES_DIR, DATA_DIR, BASE_DIR]

    for folder in search_dirs:
        candidate = folder / filename
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Arquivo '{filename}' não encontrado nas pastas "
        f"{[str(d) for d in search_dirs]}"
    )


def get_db_path_objetivos() -> Path:
    """
    Retorna o caminho absoluto do banco de Objetivos.
    Pelo tree que você mandou, ele está em: pages/DBV Capital_Objetivos.db
    """
    return _find_file("DBV Capital_Objetivos.db")


def get_db_path_positivador_mtd() -> Path:
    """
    Retorna o caminho absoluto do banco do Positivador MTD.
    Pelo tree que você mandou, ele está em: pages/DBV Capital_Positivador_MTD.db
    """
    return _find_file("DBV Capital_Positivador_MTD.db")


def get_db_path_auc_mesa_rv() -> Path:
    """
    Exemplo para outro banco .db (caso você venha a usar).
    Ajuste o nome conforme o arquivo real.
    """
    return _find_file("DBV Capital_AUC Mesa RV.db")


# =============================================================================
# FUNÇÕES GENÉRICAS DE LEITURA
# =============================================================================

def _connect(db_path: Path) -> sqlite3.Connection:
    """Abre conexão SQLite com o caminho informado."""
    return sqlite3.connect(db_path)


def read_sql(
    query: str,
    db_path: Path,
    params: Optional[dict | tuple] = None
) -> pd.DataFrame:
    """
    Executa uma query SQL e devolve um DataFrame.
    Uso básico: df = read_sql("SELECT * FROM tabela", get_db_path_objetivos())
    """
    conn = _connect(db_path)
    try:
        if params is None:
            df = pd.read_sql_query(query, conn)
        else:
            df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df


# =============================================================================
# VERSÕES COM CACHE (para usar em dashboards Streamlit)
# =============================================================================

@lru_cache(maxsize=32)
def cached_query_objetivos(query: str) -> pd.DataFrame:
    """
    Executa uma query no banco de Objetivos com cache em memória.
    Útil para não ficar abrindo o banco toda hora no Streamlit.
    """
    db_path = get_db_path_objetivos()
    return read_sql(query, db_path)


@lru_cache(maxsize=32)
def cached_query_positivador_mtd(query: str) -> pd.DataFrame:
    """
    Executa uma query no banco do Positivador MTD com cache em memória.
    """
    db_path = get_db_path_positivador_mtd()
    return read_sql(query, db_path)


@lru_cache(maxsize=32)
def cached_query_generic(query: str, filename: str) -> pd.DataFrame:
    """
    Query genérica que recebe o nome do arquivo .db e faz a busca.
    Exemplo:
        df = cached_query_generic(
            "SELECT * FROM Tabela",
            "DBV Capital_Objetivos.db"
        )
    """
    db_path = _find_file(filename)
    return read_sql(query, db_path)


# =============================================================================
# FUNÇÕES AUXILIARES (CSV EXPORT ETC.)
# =============================================================================

def ensure_csv_export_dir() -> Path:
    """
    Garante que a pasta csv_export exista e retorna o Path.
    """
    CSV_EXPORT_DIR.mkdir(exist_ok=True)
    return CSV_EXPORT_DIR


def export_df_to_csv(df: pd.DataFrame, filename: str) -> Path:
    """
    Salva um DataFrame em csv_export/filename e retorna o caminho.
    """
    export_dir = ensure_csv_export_dir()
    file_path = export_dir / filename
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    return file_path
