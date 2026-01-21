"""
Debug do fluxo exato do dashboard para identificar onde está o erro
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
    st.title("🔍 Debug do Fluxo do Dashboard")
    st.write("Simulando exatamente o fluxo do dashboard principal.")
    
    # Importar as mesmas funções do dashboard
    try:
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto as carregar_dados_objetivos_pj1,
            obter_dados_captacao_mes_robusto as obter_dados_captacao_mes,
            obter_dados_captacao_ano_robusto as obter_dados_captacao_ano,
            obter_dados_auc_2026_robusto as obter_dados_auc_2026
        )
        st.success("✅ Funções importadas")
    except Exception as e:
        st.error(f"❌ Erro ao importar: {e}")
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
    
    st.subheader("🔍 Simulação do Card CAPTAÇÃO LÍQUIDA MÊS")
    
    # Código EXATO do dashboard
    st.write("### Executando código exato do dashboard:")
    
    # Carregar dados da Objetivos_PJ1
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    st.write(f"df_objetivos_pj1 carregado: {df_objetivos_pj1 is not None and not df_objetivos_pj1.empty}")
    
    # NOVA LÓGICA: Usar dados da Objetivos_PJ1
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        st.write("✅ Entrou na nova lógica")
        
        objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        obj_total_mes = objetivo_total_mes
        threshold_mes = projetado_mes
        
        st.write(f"objetivo_total_mes: {objetivo_total_mes}")
        st.write(f"projetado_mes: {projetado_mes}")
        st.write(f"obj_total_mes: {obj_total_mes}")
        st.write(f"threshold_mes: {threshold_mes}")
        
        # Definir variáveis de data para consistência
        data_atualizacao = pd.Timestamp(data_ref)
        primeiro_dia_mes = pd.Timestamp(data_atualizacao.year, data_atualizacao.month, 1)
        ultimo_dia_mes = pd.Timestamp(data_atualizacao.year, data_atualizacao.month, 1) + pd.offsets.MonthEnd(1)
        
        st.write(f"data_atualizacao: {data_atualizacao}")
        st.write(f"primeiro_dia_mes: {primeiro_dia_mes}")
        st.write(f"ultimo_dia_mes: {ultimo_dia_mes}")
        
    else:
        st.write("❌ Entrou no fallback")
        ano_atual = data_ref.year
        fallback_cap = 152_700_000.0 if ano_atual == 2025 else 0.0
        
        meta_anual = fallback_cap  # Simulado
        obj_total_mes = (meta_anual or 0.0) / 12
        threshold_mes = 0.0
        
        st.write(f"obj_total_mes (fallback): {obj_total_mes}")
        st.write(f"threshold_mes (fallback): {threshold_mes}")
    
    # Valor realizado atual
    v_mes = float(mets.get("capliq_mes", {}).get("valor", 0.0) or 0.0)
    st.write(f"v_mes (realizado): {v_mes}")
    
    # Testar formatação
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
        
        st.write("### Valores formatados:")
        st.write(f"Objetivo Total: {formatar_valor_curto(obj_total_mes)}")
        st.write(f"Projetado: {formatar_valor_curto(threshold_mes)}")
        st.write(f"Realizado: R$ {v_mes:,.2f}")
        
    except Exception as e:
        st.error(f"❌ Erro na formatação: {e}")
    
    # Diagnóstico
    st.write("### 🔍 Diagnóstico:")
    
    if obj_total_mes == 0 or threshold_mes == 0:
        st.error("❌ PROBLEMA: Valores zerados!")
        if obj_total_mes == 0:
            st.write("- obj_total_mes está zerado")
        if threshold_mes == 0:
            st.write("- threshold_mes está zerado")
    else:
        st.success("✅ Valores corretos!")
        st.write("O problema deve estar em outra parte do dashboard.")
    
    # Verificar se há algum problema com as colunas
    st.write("### 📊 Verificação dos dados:")
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        st.dataframe(df_objetivos_pj1.head(3))
        
        # Verificar dados da data específica
        data_str = data_ref.strftime('%Y-%m-%d')
        dados_data = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d') == data_str]
        
        if not dados_data.empty:
            st.write(f"Dados para {data_str}:")
            st.dataframe(dados_data[['Data', 'Cap Objetivo (ano)', 'Cap Acumulado', 'AUC Objetivo (Ano)', 'AUC Acumulado']])

if __name__ == "__main__":
    main()
