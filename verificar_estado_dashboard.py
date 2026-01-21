"""
Verificar o estado real do dashboard para identificar o problema
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

def verificar_dashboard():
    st.title("🔍 Verificação do Estado do Dashboard")
    st.write("Este script ajuda a identificar por que os valores dos cards estão incorretos.")
    
    # Adicionar path
    sys.path.append(str(Path(__file__).parent))
    
    try:
        # Importar funções robustas
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto,
            obter_dados_captacao_mes_robusto,
            obter_dados_captacao_ano_robusto,
            obter_dados_auc_2026_robusto
        )
        
        st.success("✅ Funções robustas importadas")
        
        # Data de referência
        data_ref = datetime(2026, 1, 19)
        st.write(f"📅 Data de referência: {data_ref}")
        
        # Carregar dados
        with st.spinner("Carregando dados..."):
            df_objetivos_pj1 = carregar_dados_objetivos_pj1_robusto()
        
        # Verificar estado dos dados
        st.subheader("📊 Estado dos Dados")
        
        if df_objetivos_pj1 is None:
            st.error("❌ df_objetivos_pj1 é None")
            st.write("O dashboard vai usar o fallback (lógica antiga)")
            return
        elif df_objetivos_pj1.empty:
            st.error("❌ df_objetivos_pj1 está vazio")
            st.write("O dashboard vai usar o fallback (lógica antiga)")
            return
        else:
            st.success(f"✅ df_objetivos_pj1 carregado: {len(df_objetivos_pj1)} registros")
            st.write(f"Colunas: {list(df_objetivos_pj1.columns)}")
            
            # Mostrar primeiros registros
            st.write("Primeiros registros:")
            st.dataframe(df_objetivos_pj1.head())
        
        # Testar as funções
        st.subheader("🧪 Teste das Funções")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**CAPTAÇÃO MÊS**")
            obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df_objetivos_pj1, data_ref)
            st.write(f"Objetivo: R$ {obj_mes:,.2f}")
            st.write(f"Projetado: R$ {proj_mes:,.2f}")
            
            if obj_mes == 0:
                st.error("⚠️ Objetivo é 0!")
            if proj_mes == 0:
                st.error("⚠️ Projetado é 0!")
            if proj_mes == 1:
                st.error("⚠️ Projetado é 1!")
        
        with col2:
            st.write("**CAPTAÇÃO ANO**")
            obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df_objetivos_pj1, data_ref)
            st.write(f"Objetivo: R$ {obj_ano:,.2f}")
            st.write(f"Projetado: R$ {proj_ano:,.2f}")
            
            if obj_ano == 0:
                st.error("⚠️ Objetivo é 0!")
            if proj_ano == 0:
                st.error("⚠️ Projetado é 0!")
            if proj_ano == 1:
                st.error("⚠️ Projetado é 1!")
        
        with col3:
            st.write("**AUC 2026**")
            obj_auc, proj_auc = obter_dados_auc_2026_robusto(df_objetivos_pj1, data_ref)
            st.write(f"Objetivo: R$ {obj_auc:,.2f}")
            st.write(f"Projetado: R$ {proj_auc:,.2f}")
            
            if obj_auc == 0:
                st.error("⚠️ Objetivo é 0!")
            if proj_auc == 0:
                st.error("⚠️ Projetado é 0!")
            if proj_auc == 1:
                st.error("⚠️ Projetado é 1!")
        
        # Verificar configuração
        st.subheader("⚙️ Configuração")
        st.write(f"**Data atual:** {datetime.now()}")
        st.write(f"**Diretório atual:** {Path.cwd()}")
        st.write(f"**Path do script:** {Path(__file__).parent}")
        
        # Verificar banco de dados
        st.subheader("🗄️ Banco de Dados")
        db_path = Path("DBV Capital_Objetivos.db")
        if db_path.exists():
            st.success(f"✅ Banco encontrado: {db_path}")
            st.write(f"Tamanho: {db_path.stat().st_size} bytes")
        else:
            st.error(f"❌ Banco não encontrado: {db_path}")
        
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    verificar_dashboard()
