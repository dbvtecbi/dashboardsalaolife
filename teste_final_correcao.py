"""
Teste final após remover a função local que sobrescrevia a importação
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    st.title("🔍 Teste Final Após Correção")
    st.write("Verificando se a remoção da função local resolveu o problema.")
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    st.write(f"📅 Data de referência: {data_ref}")
    
    # Importar as funções do dashboard (agora devem ser as robustas)
    try:
        from Dashboard_Salão_Atualizado import carregar_dados_objetivos_pj1
        st.success("✅ carregar_dados_objetivos_pj1 importado do dashboard")
        
        # Verificar se é a função robusta
        df = carregar_dados_objetivos_pj1()
        if df is not None and not df.empty:
            st.success(f"✅ Dados carregados: {len(df)} registros")
            
            # Verificar colunas
            colunas_esperadas = ['Data', 'Cap Objetivo (ano)', 'Cap Acumulado', 'AUC Objetivo (Ano)', 'AUC Acumulado']
            colunas_presentes = [col for col in colunas_esperadas if col in df.columns]
            
            st.write(f"Colunas presentes: {colunas_presentes}")
            
            if len(colunas_presentes) == len(colunas_esperadas):
                st.success("✅ Todas as colunas esperadas estão presentes!")
            else:
                st.error("❌ Colunas faltando!")
                
        else:
            st.error("❌ Dados não carregados corretamente")
            
    except Exception as e:
        st.error(f"❌ Erro ao importar ou executar: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    # Testar as outras funções
    try:
        from Dashboard_Salão_Atualizado import (
            obter_dados_captacao_mes,
            obter_dados_captacao_ano,
            obter_dados_auc_2026
        )
        
        if df is not None and not df.empty:
            st.subheader("🧪 Teste das funções:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**CAPTAÇÃO MÊS**")
                obj_mes, proj_mes = obter_dados_captacao_mes(df, data_ref)
                st.write(f"Objetivo: R$ {obj_mes:,.2f}")
                st.write(f"Projetado: R$ {proj_mes:,.2f}")
                
                if obj_mes > 0 and proj_mes > 0:
                    st.success("✅ OK")
                else:
                    st.error("❌ Zerado")
            
            with col2:
                st.write("**CAPTAÇÃO ANO**")
                obj_ano, proj_ano = obter_dados_captacao_ano(df, data_ref)
                st.write(f"Objetivo: R$ {obj_ano:,.2f}")
                st.write(f"Projetado: R$ {proj_ano:,.2f}")
                
                if obj_ano > 0 and proj_ano > 0:
                    st.success("✅ OK")
                else:
                    st.error("❌ Zerado")
            
            with col3:
                st.write("**AUC 2026**")
                obj_auc, proj_auc = obter_dados_auc_2026(df, data_ref)
                st.write(f"Objetivo: R$ {obj_auc:,.2f}")
                st.write(f"Projetado: R$ {proj_auc:,.2f}")
                
                if obj_auc > 0 and proj_auc > 0:
                    st.success("✅ OK")
                else:
                    st.error("❌ Zerado")
            
            # Verificação final
            if all(v > 0 for v in [obj_mes, proj_mes, obj_ano, proj_ano, obj_auc, proj_auc]):
                st.success("🎉 TODOS OS VALORES CORRETOS!")
                st.info("Agora execute: `streamlit run Home.py` para ver o dashboard funcionando!")
            else:
                st.error("❌ Ainda há valores zerados")
                
    except Exception as e:
        st.error(f"❌ Erro ao testar funções: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
