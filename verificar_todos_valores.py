"""
Verificar todos os valores de AUC Acumulado para encontrar o valor 465.595.358,42
"""
import sys
from pathlib import Path
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Verificando todos os valores de AUC Acumulado")
    print("=" * 60)
    
    # Importar função robusta
    try:
        from correcao_final import carregar_dados_objetivos_pj1_robusto
        print("✅ Função importada")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return
    
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
    
    # Ordenar por data
    df_sorted = df.sort_values('Data')
    
    print("\n📊 Todos os valores de AUC Acumulado:")
    print("=" * 80)
    print(f"{'Data':<12} {'AUC Acumulado':<20} {'Arredondado (1 casa)':<15} {'Arredondado (2 casas)':<15}")
    print("=" * 80)
    
    valor_procurado = 465595358.42
    encontrado = False
    
    for idx, row in df_sorted.iterrows():
        data_str = row['Data'].strftime('%Y-%m-%d')
        valor = float(row['AUC Acumulado'])
        arred1 = valor / 1_000_000
        arred2 = valor / 1_000_000
        
        # Verificar se é o valor procurado
        if abs(valor - valor_procurado) < 1000:  # Tolerância de 1.000
            print(f"{data_str:<12} {valor:>20,.2f} {arred1:>15.1f}M {arred2:>15.2f}M ⭐")
            encontrado = True
        else:
            print(f"{data_str:<12} {valor:>20,.2f} {arred1:>15.1f}M {arred2:>15.2f}M")
    
    print("=" * 80)
    
    if encontrado:
        print(f"✅ Valor {valor_procurado:,.2f} encontrado!")
    else:
        print(f"❌ Valor {valor_procurado:,.2f} NÃO encontrado nos dados")
        print(f"\n🔍 Valores mais próximos:")
        
        # Encontrar valores mais próximos
        df_sorted['diferenca'] = abs(df_sorted['AUC Acumulado'] - valor_procurado)
        proximos = df_sorted.nsmallest(3, 'diferenca')
        
        for idx, row in proximos.iterrows():
            data_str = row['Data'].strftime('%Y-%m-%d')
            valor = float(row['AUC Acumulado'])
            dif = abs(valor - valor_procurado)
            print(f"  {data_str}: {valor:,.2f} (diferença: {dif:,.2f})")
    
    # Verificar especificamente o dia 19/01/2026
    print(f"\n🎯 Verificação específica - 19/01/2026:")
    data_ref = pd.Timestamp(2026, 1, 19)
    df_data = df_sorted[df_sorted['Data'] == data_ref]
    
    if not df_data.empty:
        valor = float(df_data['AUC Acumulado'].iloc[0])
        print(f"Valor exato: {valor:,.2f}")
        print(f"Arredondado (1 casa): {valor/1_000_000:.1f}M")
        print(f"Arredondado (2 casas): {valor/1_000_000:.2f}M")
        
        # Verificar se deveria ser 465.5M
        if valor >= 465500000:
            print("✅ Deveria ser arredondado para 465.5M")
        else:
            print("❌ Deveria ser arredondado para 465.4M")

if __name__ == "__main__":
    main()
