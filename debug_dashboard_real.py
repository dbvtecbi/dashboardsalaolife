"""
Debug específico do dashboard real para identificar por que os valores estão zerados
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    st.title("🔍 Debug do Dashboard Real")
    st.write("Investigando por que os valores estão zerados no dashboard principal.")
    
    # Importar as mesmas funções do dashboard
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
    
    # Data de referência (mesma do dashboard)
    data_ref = datetime(2026, 1, 19)
    st.write(f"📅 Data de referência: {data_ref}")
    
    # Métricas simuladas (mesmas do dashboard)
    mets = {
        "capliq_mes": {"valor": 29600000.0},
        "capliq_ano": {"valor": 29600000.0},
        "auc": {"valor": 474900000.0}
    }
    
    st.subheader("🔍 Investigação Passo a Passo")
    
    # Passo 1: Carregar dados
    st.write("### 1. Carregando dados da Objetivos_PJ1")
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    
    if df_objetivos_pj1 is None:
        st.error("❌ df_objetivos_pj1 é None - vai usar fallback")
        st.write("Isso explica por que os valores são zerados!")
        return
    elif df_objetivos_pj1.empty:
        st.error("❌ df_objetivos_pj1 está vazio - vai usar fallback")
        st.write("Isso explica por que os valores são zerados!")
        return
    else:
        st.success(f"✅ df_objetivos_pj1 carregado: {len(df_objetivos_pj1)} registros")
        st.dataframe(df_objetivos_pj1.head(3))
    
    # Passo 2: Testar as funções individualmente
    st.write("### 2. Testando as funções individualmente")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**obter_dados_captacao_mes**")
        try:
            obj_mes, proj_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
            st.write(f"Retorno: ({obj_mes}, {proj_mes})")
            st.write(f"Objetivo: R$ {obj_mes:,.2f}")
            st.write(f"Projetado: R$ {proj_mes:,.2f}")
            
            if obj_mes == 0 or proj_mes == 0:
                st.error("⚠️ Função retornou 0!")
            else:
                st.success("✅ Função OK")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
    
    with col2:
        st.write("**obter_dados_captacao_ano**")
        try:
            obj_ano, proj_ano = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
            st.write(f"Retorno: ({obj_ano}, {proj_ano})")
            st.write(f"Objetivo: R$ {obj_ano:,.2f}")
            st.write(f"Projetado: R$ {proj_ano:,.2f}")
            
            if obj_ano == 0 or proj_ano == 0:
                st.error("⚠️ Função retornou 0!")
            else:
                st.success("✅ Função OK")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
    
    with col3:
        st.write("**obter_dados_auc_2026**")
        try:
            obj_auc, proj_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
            st.write(f"Retorno: ({obj_auc}, {proj_auc})")
            st.write(f"Objetivo: R$ {obj_auc:,.2f}")
            st.write(f"Projetado: R$ {proj_auc:,.2f}")
            
            if obj_auc == 0 or proj_auc == 0:
                st.error("⚠️ Função retornou 0!")
            else:
                st.success("✅ Função OK")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
    
    # Passo 3: Simular o fluxo exato do dashboard
    st.write("### 3. Simulando o fluxo exato do dashboard")
    
    st.write("**Simulação do card CAPTAÇÃO LÍQUIDA MÊS:**")
    
    # Código exato do dashboard
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        st.write("✅ Entrou na nova lógica")
        objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        obj_total_mes = objetivo_total_mes
        threshold_mes = projetado_mes
        
        st.write(f"objetivo_total_mes: {objetivo_total_mes}")
        st.write(f"projetado_mes: {projetado_mes}")
        st.write(f"obj_total_mes: {obj_total_mes}")
        st.write(f"threshold_mes: {threshold_mes}")
        
        # Verificar se os valores são zero
        if obj_total_mes == 0:
            st.error("❌ obj_total_mes é 0!")
        if threshold_mes == 0:
            st.error("❌ threshold_mes é 0!")
        if threshold_mes == 1:
            st.error("❌ threshold_mes é 1!")
            
    else:
        st.write("❌ Entrou no fallback")
        ano_atual = data_ref.year
        fallback_cap = 152_700_000.0 if ano_atual == 2025 else 0.0
        
        meta_anual = 152_700_000.0  # Simulado
        obj_total_mes = (meta_anual or 0.0) / 12
        threshold_mes = 0.0
        
        st.write(f"obj_total_mes (fallback): {obj_total_mes}")
        st.write(f"threshold_mes (fallback): {threshold_mes}")
    
    # Passo 4: Testar formatação
    st.write("### 4. Testando formatação")
    
    try:
        # Importar função formatar_valor_curto do dashboard
        with open('pages/Dashboard_Salão_Atualizado.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        inicio = conteudo.find('def formatar_valor_curto')
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
        
        st.write(f"obj_total_mes formatado: {formatar_valor_curto(obj_total_mes)}")
        st.write(f"threshold_mes formatado: {formatar_valor_curto(threshold_mes)}")
        
    except Exception as e:
        st.error(f"❌ Erro na formatação: {e}")
    
    # Diagnóstico final
    st.write("### 5. Diagnóstico Final")
    
    if obj_total_mes == 0 or threshold_mes == 0:
        st.error("❌ PROBLEMA IDENTIFICADO: Valores estão zerados!")
        st.write("Possíveis causas:")
        st.write("1. As funções estão retornando 0")
        st.write("2. Está caindo no fallback (lógica antiga)")
        st.write("3. Há algum erro no fluxo do dashboard")
    else:
        st.success("✅ Valores estão corretos!")
        st.write("O problema pode estar em outra parte do dashboard.")

if __name__ == "__main__":
    main()
