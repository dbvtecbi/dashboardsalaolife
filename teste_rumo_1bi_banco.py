"""
Teste do RUMO A 1BI pegando objetivo do banco de dados (01/01/2027)
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Teste RUMO A 1BI - Objetivo do Banco de Dados")
    print("=" * 60)
    
    # Importar função robusta
    try:
        from correcao_final import carregar_dados_objetivos_pj1_robusto
        print("✅ Função importada")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    print(f"📅 Data de referência: {data_ref}")
    
    # Carregar dados
    try:
        df = carregar_dados_objetivos_pj1_robusto()
        if df is not None and not df.empty:
            print(f"✅ Dados carregados: {len(df)} registros")
        else:
            print("❌ Dados não carregados")
            return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Garantir que Data seja datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Data']):
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Verificar se há dados para 2027
    print(f"\n🔍 Verificando dados para 01/01/2027:")
    
    data_2027 = pd.Timestamp(2027, 1, 1)
    df_2027 = df[df['Data'].dt.year == 2027]
    
    if not df_2027.empty:
        print(f"✅ Encontrados {len(df_2027)} registros para 2027")
        print("\n📊 Dados de 2027:")
        for idx, row in df_2027.iterrows():
            print(f"Data: {row['Data']}")
            print(f"AUC Objetivo (Ano): {row['AUC Objetivo (Ano)']}")
            print(f"AUC Acumulado: {row['AUC Acumulado']}")
            print("-" * 30)
        
        # Pegar o primeiro dia de 2027
        df_2027_sorted = df_2027.sort_values('Data')
        objetivo_banco = float(df_2027_sorted['AUC Objetivo (Ano)'].iloc[0])
        
        print(f"\n🎯 Objetivo do banco (01/01/2027): R$ {objetivo_banco:,.2f}")
        print(f"Arredondado: R$ {objetivo_banco/1_000_000:.1f}M")
        
    else:
        print(f"❌ Nenhum registro encontrado para 2027")
        print("\n🔍 Usando projeção com base nos dados existentes:")
        
        # Mostrar último valor disponível
        df_sorted = df.sort_values('Data')
        if not df_sorted.empty:
            ultimo_registro = df_sorted.iloc[-1]
            ultimo_valor = float(ultimo_registro['AUC Objetivo (Ano)'])
            ultima_data = ultimo_registro['Data']
            
            print(f"Último valor disponível: {ultimo_valor:,.2f} ({ultima_data.strftime('%d/%m/%Y')})")
            
            # Aplicar crescimento estimado
            crescimento_estimado = 1.10  # 10% de crescimento
            objetivo_projetado = ultimo_valor * crescimento_estimado
            
            print(f"Projeção para 2027 (+10%): R$ {objetivo_projetado:,.2f}")
            print(f"Arredondado: R$ {objetivo_projetado/1_000_000:.1f}M")
            
            objetivo_banco = objetivo_projetado
        else:
            print("❌ Nenhum dado disponível para projeção")
            return
    
    # Testar a função obter_dados_rumo_1bi
    try:
        from correcao_final import obter_dados_rumo_1bi_robusto
        
        objetivo_func, projetado_func = obter_dados_rumo_1bi_robusto(df, data_ref)
        
        print(f"\n🧪 Resultados da função:")
        print(f"Objetivo Total: R$ {objetivo_func:,.2f} ({objetivo_func/1_000_000:.1f}M)")
        print(f"Projetado: R$ {projetado_func:,.2f} ({projetado_func/1_000_000:.1f}M)")
        
        # Verificar se o objetivo bate com o banco
        if abs(objetivo_func - objetivo_banco) < 1000:
            print("✅ Objetivo da função igual ao banco de dados!")
        else:
            print("⚠️ Objetivo da função diferente do banco de dados")
        
        # Comparar com AUC-2026
        from correcao_final import obter_dados_auc_2026_robusto
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        
        print(f"\n📈 Comparação final:")
        print(f"AUC-2026 - Objetivo: R$ {obj_auc:,.2f} ({obj_auc/1_000_000:.1f}M)")
        print(f"AUC-2026 - Projetado: R$ {proj_auc:,.2f} ({proj_auc/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Objetivo: R$ {objetivo_func:,.2f} ({objetivo_func/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Projetado: R$ {projetado_func:,.2f} ({projetado_func/1_000_000:.1f}M)")
        
        if abs(projetado_func - proj_auc) < 1000:
            print("✅ Projetado igual ao AUC-2026 (conforme solicitado)")
        else:
            print("⚠️ Projetado diferente do AUC-2026")
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🎉 Teste concluído!")
    print("Execute: `streamlit run Home.py` para ver no dashboard.")

if __name__ == "__main__":
    main()
