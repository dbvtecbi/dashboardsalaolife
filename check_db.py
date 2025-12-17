#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
check_db.py
----------------------------------------
Inspeciona um banco SQLite:
- Lista tabelas com número de linhas
- Mostra schema (PRAGMA table_info)
- Lista índices (PRAGMA index_list / index_info)
- Mostra nulos por coluna
- Mostra amostra de linhas
- (Opcional) estatísticas básicas para colunas numéricas

Uso:
  python check_db.py --db caminho/do/arquivo.db
  python check_db.py --db arquivo.db --table objetivos_pj1
  python check_db.py --db arquivo.db --like obj% --limit 20
"""

import argparse
import os
import sqlite3
import sys
from textwrap import indent

import pandas as pd


def connect(db_path: str) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        print(f"Arquivo não encontrado: {db_path}", file=sys.stderr)
        sys.exit(1)
    return sqlite3.connect(db_path)


def list_tables(conn: sqlite3.Connection, like: str | None = None) -> list[str]:
    cur = conn.cursor()
    if like:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ORDER BY name;",
            (like,)
        )
    else:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [r[0] for r in cur.fetchall()]


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM [{table}]")
    return cur.fetchone()[0]


def get_schema(conn: sqlite3.Connection, table: str) -> pd.DataFrame:
    return pd.read_sql_query(f"PRAGMA table_info([{table}]);", conn)


def get_indexes(conn: sqlite3.Connection, table: str) -> pd.DataFrame:
    idx_list = pd.read_sql_query(f"PRAGMA index_list([{table}]);", conn)
    rows = []
    for _, r in idx_list.iterrows():
        idx_name = r["name"]
        info = pd.read_sql_query(f"PRAGMA index_info([{idx_name}]);", conn)
        rows.append({"index_name": idx_name, "unique": r.get("unique", None), "columns": ",".join(info["name"])})
    return pd.DataFrame(rows)


def null_counts(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum().sort_values(ascending=False)


def numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include="number")
    if num.empty:
        return pd.DataFrame()
    desc = num.describe().T  # count, mean, std, min, 25%, 50%, 75%, max
    return desc


def sample_rows(conn: sqlite3.Connection, table: str, limit: int = 10) -> pd.DataFrame:
    return pd.read_sql_query(f"SELECT * FROM [{table}] LIMIT {int(limit)};", conn)


def human_size(path: str) -> str:
    b = os.path.getsize(path)
    for unit in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def main():
    ap = argparse.ArgumentParser(description="Inspeciona um banco SQLite rapidamente.")
    ap.add_argument("--db", required=True, help="Caminho do arquivo .db")
    ap.add_argument("--table", help="Nome exato da tabela a inspecionar (opcional)")
    ap.add_argument("--like", help="Filtro LIKE para nomes de tabela (ex.: obj%%) (opcional)")
    ap.add_argument("--limit", type=int, default=10, help="Linhas de amostra por tabela (padrão: 10)")
    args = ap.parse_args()

    print(f"Arquivo: {args.db} ({human_size(args.db)})")
    conn = connect(args.db)

    # Tabelas
    tables = list_tables(conn, like=args.like)
    if not tables:
        print("Nenhuma tabela encontrada.")
        return

    # Se foi passada uma tabela específica, prioriza ela
    if args.table:
        if args.table not in tables:
            print(f"Tabela '{args.table}' não encontrada. Disponíveis: {', '.join(tables)}")
            return
        tables = [args.table]

    # Sumário
    print("\n== Sumário de Tabelas ==")
    for t in tables:
        try:
            n = count_rows(conn, t)
        except Exception as e:
            n = f"erro: {e}"
        print(f"- {t}: {n} linhas")

    # Detalhes
    for t in tables:
        print(f"\n====================\nTabela: {t}")
        # Schema
        try:
            schema = get_schema(conn, t)
            print("\nSchema (PRAGMA table_info):")
            print(indent(schema.to_string(index=False), "  "))
        except Exception as e:
            print(f"  Erro ao obter schema: {e}")

        # Índices
        try:
            idx = get_indexes(conn, t)
            print("\nÍndices:")
            if idx.empty:
                print("  (nenhum índice)")
            else:
                print(indent(idx.to_string(index=False), "  "))
        except Exception as e:
            print(f"  Erro ao obter índices: {e}")

        # Amostra
        try:
            df_sample = sample_rows(conn, t, limit=args.limit)
            print(f"\nAmostra (primeiras {args.limit} linhas):")
            print(indent(df_sample.head(args.limit).to_string(index=False), "  "))

            # Nulos por coluna
            print("\nNulos por coluna:")
            nc = null_counts(df_sample)
            print(indent(nc.to_string(), "  "))

            # Estatísticas numéricas
            stats = numeric_stats(df_sample)
            if not stats.empty:
                print("\nEstatísticas numéricas (amostra):")
                print(indent(stats.to_string(), "  "))
        except Exception as e:
            print(f"  Erro ao ler amostra: {e}")

    conn.close()
    print("\nFeito.")

if __name__ == "__main__":
    main()
