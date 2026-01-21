"""
Comparar as funções formatar_valor_curto do dashboard e do debug
"""
import sys
from pathlib import Path

# Adicionar path
sys.path.append(str(Path('.').absolute() / 'pages'))

# Importar a função do dashboard principal
try:
    # Ler o arquivo do dashboard e extrair a função formatar_valor_curto
    with open('pages/Dashboard_Salão_Atualizado.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar a função formatar_valor_curto
    inicio = conteudo.find('def formatar_valor_curto')
    if inicio == -1:
        print("❌ Função formatar_valor_curto não encontrada no dashboard")
        sys.exit(1)
    
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
    
    funcao_dashboard = conteudo[inicio:pos].strip()
    print("🔍 Função formatar_valor_curto do DASHBOARD:")
    print(funcao_dashboard)
    print()
    
    # Executar a função do dashboard
    namespace_dashboard = {}
    exec(funcao_dashboard, namespace_dashboard)
    formatar_dashboard = namespace_dashboard['formatar_valor_curto']
    
    # Nossa função do debug
    def formatar_debug(valor):
        try:
            v = float(valor or 0)
        except (ValueError, TypeError):
            return "R$ 0"
        
        if v >= 1_000_000_000:
            return f"R$ {v / 1_000_000_000:,.1f}bi"
        if v >= 1_000_000:
            return f"R$ {v / 1_000_000:,.1f}M"
        if v >= 1_000:
            return f"R$ {v / 1_000:,.1f}K"
        return f"R$ {v:,.0f}"
    
    print("🔍 Função formatar_valor_curto do DEBUG:")
    print(formatar_debug)
    print()
    
    # Testar ambas as funções
    valores_teste = [
        15589793.17126484,  # CAPTAÇÃO MÊS objetivo
        9550752.759616392,  # CAPTAÇÃO MÊS projetado
        183600000.0,        # CAPTAÇÃO ANO objetivo
        694000000.0,         # AUC 2026 objetivo
        0,                   # Zero
        1                    # Um
    ]
    
    print("🧪 COMPARAÇÃO DAS FUNÇÕES:")
    print("=" * 80)
    print(f"{'Valor':<20} {'Dashboard':<20} {'Debug':<20} {'Igual?':<10}")
    print("=" * 80)
    
    for val in valores_teste:
        resultado_dashboard = formatar_dashboard(val)
        resultado_debug = formatar_debug(val)
        igual = "✅" if resultado_dashboard == resultado_debug else "❌"
        
        print(f"{val:<20.2f} {resultado_dashboard:<20} {resultado_debug:<20} {igual:<10}")
    
    print("\n🔍 ANÁLISE:")
    if all(formatar_dashboard(v) == formatar_debug(v) for v in valores_teste):
        print("✅ As funções são IDÊNTICAS - o problema não está na formatação!")
    else:
        print("❌ As funções são DIFERENTES - este pode ser o problema!")
    
    # Testar específico os valores que estão aparecendo como R$ 0 e R$ 1
    print(f"\n🎯 Teste específico:")
    print(f"Valor 15589793.17:")
    print(f"  Dashboard: {formatar_dashboard(15589793.17126484)}")
    print(f"  Debug: {formatar_debug(15589793.17126484)}")
    
    print(f"Valor 9550752.76:")
    print(f"  Dashboard: {formatar_dashboard(9550752.759616392)}")
    print(f"  Debug: {formatar_debug(9550752.759616392)}")

except Exception as e:
    print(f"❌ Erro ao analisar: {e}")
    import traceback
    traceback.print_exc()
