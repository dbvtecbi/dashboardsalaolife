import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import sqlite3

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

# Importar funções
try:
    from funcoes_objetivos_pj1 import (
        carregar_dados_objetivos_pj1,
        obter_dados_captacao_ano,
        obter_dados_auc_2026,
        obter_dados_captacao_mes,
        obter_cap_diario_verificacao
    )
    st.success("✅ Importações realizadas com sucesso")
except ImportError as e:
    st.error(f"❌ Erro na importação: {e}")
    st.stop()

st.title("🧪 Teste das Novas Funcionalidades do Dashboard")

# Data de referência
data_ref = datetime(2026, 1, 19)
st.write(f"📅 Data de referência: {data_ref.strftime('%d/%m/%Y')}")

# Botão para recarregar dados
if st.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()

# Testar carregamento
st.subheader("1. Carregamento de Dados")
with st.spinner("Carregando dados..."):
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()

if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
    st.success(f"✅ Dados carregados: {len(df_objetivos_pj1)} registros")
    st.write(f"Colunas: {list(df_objetivos_pj1.columns)}")
    st.dataframe(df_objetivos_pj1.head(3))
else:
    st.error("❌ Erro ao carregar dados")
    st.stop()

# Testar cada card
st.subheader("2. Teste dos Cards")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 CAPTAÇÃO LÍQUIDA ANO")
    try:
        objetivo_total, projetado_acumulado = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
        st.metric("Objetivo Total", f"R$ {objetivo_total:,.2f}")
        st.metric("Projetado Acumulado", f"R$ {projetado_acumulado:,.2f}")
        st.success("✅ Funcionando")
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        st.code(str(e))

with col2:
    st.markdown("### 📈 AUC - 2026")
    try:
        objetivo_total_auc, projetado_acumulado_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
        st.metric("Objetivo Total AUC", f"R$ {objetivo_total_auc:,.2f}")
        st.metric("Projetado Acumulado AUC", f"R$ {projetado_acumulado_auc:,.2f}")
        st.success("✅ Funcionando")
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        st.code(str(e))

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 📅 CAPTAÇÃO LÍQUIDA MÊS")
    try:
        objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        st.metric("Objetivo Total Mês", f"R$ {objetivo_total_mes:,.2f}")
        st.metric("Projetado Mês", f"R$ {projetado_mes:,.2f}")
        st.success("✅ Funcionando")
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        st.code(str(e))

with col4:
    st.markdown("### 🔍 CAP DIÁRIO (Verificação)")
    try:
        cap_diario = obter_cap_diario_verificacao(df_objetivos_pj1, data_ref)
        st.metric("CAP Diário", f"R$ {cap_diario:,.2f}")
        st.success("✅ Funcionando")
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        st.code(str(e))

# Resumo
st.subheader("3. Resumo dos Valores")
try:
    objetivo_total, projetado_acumulado = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
    objetivo_total_auc, projetado_acumulado_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
    objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
    cap_diario = obter_cap_diario_verificacao(df_objetivos_pj1, data_ref)
    
    st.markdown(f"""
    - **CAPTAÇÃO ANO:** Objetivo R$ {objetivo_total:,.2f} | Projetado R$ {projetado_acumulado:,.2f}
    - **AUC 2026:** Objetivo R$ {objetivo_total_auc:,.2f} | Projetado R$ {projetado_acumulado_auc:,.2f}
    - **CAPTAÇÃO MÊS:** Objetivo R$ {objetivo_total_mes:,.2f} | Projetado R$ {projetado_mes:,.2f}
    - **CAP DIÁRIO:** R$ {cap_diario:,.2f}
    """)
    
    # Verificar consistência
    if projetado_mes <= projetado_acumulado:
        st.success("✅ Consistência: Projetado mês ≤ Projetado ano")
    else:
        st.error("❌ Inconsistência: Projetado mês > Projetado ano")
        
except Exception as e:
    st.error(f"❌ Erro no resumo: {e}")
    st.code(str(e))
