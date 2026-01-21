"""
Teste final do dashboard com todas as alterações aplicadas
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar path
sys.path.append(str(Path(__file__).parent))

# Importar as funções corrigidas do dashboard
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    st.title("🔍 Teste Final do Dashboard")
    st.write("Verificando se todas as alterações foram aplicadas corretamente.")
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    st.write(f"📅 Data de referência: {data_ref}")
    
    # Importar funções robustas
    try:
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto as carregar_dados_objetivos_pj1,
            obter_dados_captacao_mes_robusto as obter_dados_captacao_mes,
            obter_dados_captacao_ano_robusto as obter_dados_captacao_ano,
            obter_dados_auc_2026_robusto as obter_dados_auc_2026
        )
        st.success("✅ Funções robustas importadas")
    except Exception as e:
        st.error(f"❌ Erro ao importar funções: {e}")
        return
    
    # Importar função formatar_valor_curto do dashboard
    try:
        # Ler apenas a função formatar_valor_curto do dashboard
        with open('pages/Dashboard_Salão_Atualizado.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Encontrar e extrair a função formatar_valor_curto
        inicio = conteudo.find('def formatar_valor_curto')
        if inicio == -1:
            st.error("❌ Função formatar_valor_curto não encontrada")
            return
        
        # Encontrar o fim da função
        pos = inicio
        nivel = 0
        while pos < len(conteudo):
            if conteudo[pos] == '\n':
                nivel = 0
            elif conteudo[pos] == ' ':
                if nivel == 0:
                    break
            pos += 1
        
        funcao_str = conteudo[inicio:pos].strip()
        namespace = {}
        exec(funcao_str, namespace)
        formatar_valor_curto = namespace['formatar_valor_curto']
        st.success("✅ Função formatar_valor_curto importada")
        
    except Exception as e:
        st.error(f"❌ Erro ao importar formatar_valor_curto: {e}")
        return
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    
    # Verificar estado dos dados
    if df_objetivos_pj1 is None or df_objetivos_pj1.empty:
        st.error("❌ Dados não carregados corretamente")
        return
    
    st.success(f"✅ Dados carregados: {len(df_objetivos_pj1)} registros")
    
    # Testar todos os cards
    st.subheader("🧪 Teste dos Cards")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**CAPTAÇÃO MÊS**")
        obj_mes, proj_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        st.write(f"Objetivo: {formatar_valor_curto(obj_mes)}")
        st.write(f"Projetado: {formatar_valor_curto(proj_mes)}")
        
        # Verificação
        if obj_mes > 0 and proj_mes > 0 and proj_mes != 1:
            st.success("✅ Valores OK")
        else:
            st.error("❌ Valores incorretos")
    
    with col2:
        st.write("**CAPTAÇÃO ANO**")
        obj_ano, proj_ano = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
        st.write(f"Objetivo: {formatar_valor_curto(obj_ano)}")
        st.write(f"Projetado: {formatar_valor_curto(proj_ano)}")
        
        # Verificação
        if obj_ano > 0 and proj_ano > 0 and proj_ano != 1:
            st.success("✅ Valores OK")
        else:
            st.error("❌ Valores incorretos")
    
    with col3:
        st.write("**AUC 2026**")
        obj_auc, proj_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
        st.write(f"Objetivo: {formatar_valor_curto(obj_auc)}")
        st.write(f"Projetado: {formatar_valor_curto(proj_auc)}")
        
        # Verificação
        if obj_auc > 0 and proj_auc > 0 and proj_auc != 1:
            st.success("✅ Valores OK")
        else:
            st.error("❌ Valores incorretos")
    
    # Resumo final
    st.subheader("📋 Resumo Final")
    
    # Valores esperados
    valores_esperados = {
        "CAPTAÇÃO MÊS": ("R$ 15.6M", "R$ 9.6M"),
        "CAPTAÇÃO ANO": ("R$ 183.6M", "R$ 9.6M"),
        "AUC 2026": ("R$ 694.0M", "R$ 465.4M")
    }
    
    resultados = {
        "CAPTAÇÃO MÊS": (formatar_valor_curto(obj_mes), formatar_valor_curto(proj_mes)),
        "CAPTAÇÃO ANO": (formatar_valor_curto(obj_ano), formatar_valor_curto(proj_ano)),
        "AUC 2026": (formatar_valor_curto(obj_auc), formatar_valor_curto(proj_auc))
    }
    
    tudo_ok = True
    
    for card, (esperado_obj, esperado_proj) in valores_esperados.items():
        resultado_obj, resultado_proj = resultados[card]
        
        if resultado_obj == esperado_obj and resultado_proj == esperado_proj:
            st.success(f"✅ {card}: {resultado_obj} | {resultado_proj}")
        else:
            st.error(f"❌ {card}: {resultado_obj} | {resultado_proj} (esperado: {esperado_obj} | {esperado_proj})")
            tudo_ok = False
    
    if tudo_ok:
        st.success("🎉 Todos os cards estão funcionando perfeitamente!")
        st.info("Agora execute: `streamlit run Home.py` para ver o dashboard principal funcionando!")
    else:
        st.error("❌ Ainda há problemas que precisam ser corrigidos.")

if __name__ == "__main__":
    main()
