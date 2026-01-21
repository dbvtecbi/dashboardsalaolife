import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

print("🔍 Debug do Erro KeyError: 'Data'")
print("=" * 50)

try:
    from funcoes_objetivos_pj1 import (
        carregar_dados_objetivos_pj1,
        obter_dados_captacao_mes
    )
    print("✅ Importações OK")
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

# Data de referência igual à do erro
data_ref = datetime(2026, 1, 19)
print(f"📅 Data de referência: {data_ref}")

print("\n1. Carregando dados...")
try:
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    if df_objetivos_pj1 is None:
        print("❌ df_objetivos_pj1 é None")
        sys.exit(1)
    if df_objetivos_pj1.empty:
        print("❌ df_objetivos_pj1 está vazio")
        sys.exit(1)
    
    print(f"✅ Dados carregados: {len(df_objetivos_pj1)} registros")
    print(f"   Colunas: {list(df_objetivos_pj1.columns)}")
    print(f"   Tipo: {type(df_objetivos_pj1)}")
    
    # Verificar se 'Data' está nas colunas
    if 'Data' in df_objetivos_pj1.columns:
        print("✅ Coluna 'Data' encontrada")
    else:
        print("❌ Coluna 'Data' NÃO encontrada")
        print(f"   Colunas disponíveis: {list(df_objetivos_pj1.columns)}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Testando obter_dados_captacao_mes...")
try:
    objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
    print(f"✅ Sucesso: Objetivo={objetivo_total_mes}, Projetado={projetado_mes}")
except Exception as e:
    print(f"❌ Erro em obter_dados_captacao_mes: {e}")
    import traceback
    traceback.print_exc()
    
print("\n3. Verificação manual...")
try:
    # Simular exatamente o que acontece dentro da função
    df = df_objetivos_pj1
    print(f"   DataFrame type: {type(df)}")
    print(f"   DataFrame empty: {df.empty}")
    print(f"   DataFrame columns: {list(df.columns)}")
    
    # Verificar acesso à coluna
    if 'Data' in df.columns:
        print("✅ 'Data' está em df.columns")
        data_col = df['Data']
        print(f"   Data column type: {type(data_col)}")
        print(f"   Data column dtype: {data_col.dtype}")
        
        # Tentar o filtro que causa o erro
        print("   Tentando filtro por mês...")
        df_mes = df[(df['Data'].dt.year == data_ref.year) & (df['Data'].dt.month == data_ref.month)]
        print(f"✅ Filtro funcionou: {len(df_mes)} registros")
        
    else:
        print("❌ 'Data' não está em df.columns")
        
except Exception as e:
    print(f"❌ Erro na verificação manual: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🔍 Fim do Debug")
