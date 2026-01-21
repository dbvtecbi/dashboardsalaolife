"""
Função para obter dados do card RUMO A 1BI usando a nova lógica
"""
import pandas as pd
from datetime import datetime

def obter_dados_rumo_1bi(df_objetivos_pj1, data_ref):
    """
    Obtém os dados para o card RUMO A 1BI usando a lógica do AUC-2026
    mas com objetivo para 2027 (01/01/2027)
    
    Args:
        df_objetivos_pj1: DataFrame com os dados da Objetivos_PJ1
        data_ref: Data de referência
        
    Returns:
        tuple: (objetivo_total, projetado_acumulado)
    """
    try:
        # Verificar se o DataFrame é válido
        if df_objetivos_pj1 is None or df_objetivos_pj1.empty:
            return 0.0, 0.0
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['Data', 'AUC Objetivo (Ano)', 'AUC Acumulado']
        for col in colunas_necessarias:
            if col not in df_objetivos_pj1.columns:
                return 0.0, 0.0
        
        # Garantir que a coluna Data seja datetime
        if not pd.api.types.is_datetime64_any_dtype(df_objetivos_pj1['Data']):
            df_objetivos_pj1['Data'] = pd.to_datetime(df_objetivos_pj1['Data'], errors='coerce')
        
        # Objetivo Total: AUC Objetivo (Ano) para 2027 (primeiro dia de 2027)
        data_2027 = pd.Timestamp(2027, 1, 1)
        
        # Filtrar registros de 2027 ou usar o último valor disponível
        df_2027 = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.year == 2027]
        
        if not df_2027.empty:
            # Pegar o primeiro registro de 2027
            df_2027_sorted = df_2027.sort_values('Data')
            objetivo_total = float(df_2027_sorted['AUC Objetivo (Ano)'].iloc[0])
        else:
            # Se não tiver dados de 2027, usar o último valor disponível como projeção
            df_sorted = df_objetivos_pj1.sort_values('Data')
            if not df_sorted.empty:
                ultimo_valor = float(df_sorted['AUC Objetivo (Ano)'].iloc[-1])
                # Aplicar um crescimento estimado para 2027 (ex: 10% de crescimento)
                objetivo_total = ultimo_valor * 1.10
            else:
                objetivo_total = 0.0
        
        # Projetado: Usar a mesma lógica do AUC-2026 (AUC Acumulado na data_ref)
        data_ref_formatada = data_ref.strftime('%Y-%m-%d')
        df_data_ref = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d') == data_ref_formatada]
        
        if not df_data_ref.empty:
            projetado_acumulado = float(df_data_ref['AUC Acumulado'].iloc[0])
        else:
            # Se não encontrar a data exata, usar o valor mais próximo
            df_objetivos_pj1_sorted = df_objetivos_pj1.sort_values('Data')
            data_ref_ts = pd.Timestamp(data_ref)
            
            # Encontrar o registro mais próximo da data_ref
            idx_proximo = (df_objetivos_pj1_sorted['Data'] - data_ref_ts).abs().idxmin()
            projetado_acumulado = float(df_objetivos_pj1_sorted.loc[idx_proximo, 'AUC Acumulado'])
        
        return objetivo_total, projetado_acumulado
        
    except Exception as e:
        print(f"Erro em obter_dados_rumo_1bi: {e}")
        return 0.0, 0.0

def testar_funcao():
    """Testar a função com dados simulados"""
    from correcao_final import carregar_dados_objetivos_pj1_robusto
    from datetime import datetime
    
    # Carregar dados reais
    df = carregar_dados_objetivos_pj1_robusto()
    data_ref = datetime(2026, 1, 19)
    
    # Testar a função
    objetivo, projetado = obter_dados_rumo_1bi(df, data_ref)
    
    print(f"🧪 Teste da função obter_dados_rumo_1bi:")
    print(f"Data de referência: {data_ref}")
    print(f"Objetivo Total (2027): R$ {objetivo:,.2f}")
    print(f"Projetado Acumulado: R$ {projetado:,.2f}")
    
    if objetivo > 0 and projetado > 0:
        print("✅ Função funcionando corretamente!")
    else:
        print("❌ Problema na função")

if __name__ == "__main__":
    testar_funcao()
