"""
Versão do dashboard com debug integrado para identificar o problema
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar path
sys.path.append(str(Path(__file__).parent))

# Importar funções robustas
from correcao_final import (
    carregar_dados_objetivos_pj1_robusto as carregar_dados_objetivos_pj1,
    obter_dados_captacao_mes_robusto as obter_dados_captacao_mes,
    obter_dados_captacao_ano_robusto as obter_dados_captacao_ano,
    obter_dados_auc_2026_robusto as obter_dados_auc_2026
)

# Função de formatação
def formatar_valor_curto(valor):
    try:
        v = float(valor or 0)
    except (ValueError, TypeError):
        return "R$ 0"
    
    if v >= 1_000_000_000:
        return f"R$ {v / 1_000_000_000:,.1f}bi"
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:,.1f}M"
    if v >= 1_000:
        return f"R$ {v / 1_000:,.1f}K"
    return f"R$ {v:,.0f}"

def main():
    st.title("🔍 Dashboard com Debug Integrado")
    st.write("Este dashboard mostra exatamente o que está acontecendo nos cards.")
    
    # Data de referência (simulando a do dashboard real)
    data_ref = datetime(2026, 1, 19)
    st.write(f"📅 Data de referência: {data_ref}")
    
    # Métricas simuladas (valores realizados)
    mets = {
        "capliq_mes": {"valor": 29600000.0},  # R$ 29,6M
        "capliq_ano": {"valor": 29600000.0},
        "auc": {"valor": 474900000.0}  # R$ 474,9M
    }
    
    st.subheader("📊 Análise dos Cards")
    
    # Carregar dados com debug
    st.write("### 1. Carregando Dados")
    with st.spinner("Carregando dados..."):
        df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    
    # Debug do estado dos dados
    if df_objetivos_pj1 is None:
        st.error("❌ df_objetivos_pj1 é None")
        st.write("Isso explicaria por que os valores são 0!")
        return
    elif df_objetivos_pj1.empty:
        st.error("❌ df_objetivos_pj1 está vazio")
        st.write("Isso explicaria por que os valores são 0!")
        return
    else:
        st.success(f"✅ df_objetivos_pj1 carregado: {len(df_objetivos_pj1)} registros")
        st.dataframe(df_objetivos_pj1.head())
    
    # Card CAPTAÇÃO LÍQUIDA MÊS
    st.write("### 2. CAPTAÇÃO LÍQUIDA MÊS")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Estado dos Dados:**")
        st.write(f"df_objetivos_pj1: {'OK' if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty else 'PROBLEMA'}")
        
        st.write("**Cálculo:**")
        if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
            st.write("Usando nova lógica (Objetivos_PJ1)")
            objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
            obj_total_mes = objetivo_total_mes
            threshold_mes = projetado_mes
        else:
            st.write("Usando fallback (lógica antiga)")
            obj_total_mes = 0.0
            threshold_mes = 0.0
        
        st.write(f"objetivo_total_mes: {objetivo_total_mes}")
        st.write(f"projetado_mes: {projetado_mes}")
        st.write(f"obj_total_mes: {obj_total_mes}")
        st.write(f"threshold_mes: {threshold_mes}")
    
    with col2:
        st.write("**Valores Formatados:**")
        st.write(f"Objetivo Total: {formatar_valor_curto(obj_total_mes)}")
        st.write(f"Projetado: {formatar_valor_curto(threshold_mes)}")
        
        # Valor realizado
        v_mes = float(mets.get("capliq_mes", {}).get("valor", 0.0) or 0.0)
        st.write(f"Realizado: R$ {v_mes:,.2f}")
    
    with col3:
        st.write("**Verificação:**")
        if obj_total_mes == 0:
            st.error("⚠️ Objetivo é 0!")
        else:
            st.success(f"✅ Objetivo OK: R$ {obj_total_mes:,.2f}")
            
        if threshold_mes == 0:
            st.error("⚠️ Projetado é 0!")
        elif threshold_mes == 1:
            st.error("⚠️ Projetado é 1!")
        else:
            st.success(f"✅ Projetado OK: R$ {threshold_mes:,.2f}")
    
    # Testar outros cards
    st.write("### 3. Outros Cards")
    
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("**CAPTAÇÃO ANO:**")
            obj_ano, proj_ano = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
            st.write(f"Objetivo: {formatar_valor_curto(obj_ano)}")
            st.write(f"Projetado: {formatar_valor_curto(proj_ano)}")
        
        with col_b:
            st.write("**AUC 2026:**")
            obj_auc, proj_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
            st.write(f"Objetivo: {formatar_valor_curto(obj_auc)}")
            st.write(f"Projetado: {formatar_valor_curto(proj_auc)}")
    
    # Informações do sistema
    st.write("### 4. Informações do Sistema")
    st.write(f"**Data atual:** {datetime.now()}")
    st.write(f"**Diretório:** {Path.cwd()}")
    st.write(f"**Python:** {sys.version}")

if __name__ == "__main__":
    main()
