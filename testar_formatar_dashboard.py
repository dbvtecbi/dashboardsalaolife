"""
Testar especificamente a função formatar_valor_curto do dashboard
"""

def formatar_valor_curto_dashboard(valor):
    try:
        v = float(valor or 0)
    except (ValueError, TypeError):
        return "R$ 0"

    if v >= 1_000_000_000:
        return f"R$ {v / 1_000_000_000:,.1f}bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:,.1f}M".replace(",", "X").replace(".", ",").replace("X", ".")
    if v >= 1_000:
        return f"R$ {v / 1_000:,.1f}K".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_valor_curto_simples(valor):
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

def main():
    print("🔍 Teste da Função formatar_valor_curto")
    print("=" * 60)
    
    # Valores que estão dando problema
    valores_teste = [
        15589793.17126484,  # Deveria ser R$ 15.6M
        9550752.759616392,  # Deveria ser R$ 9.6M
        183600000.0,        # Deveria ser R$ 183.6M
        694000000.0,         # Deveria ser R$ 694.0M
        0,                   # Deveria ser R$ 0
        1,                   # Deveria ser R$ 1
        1000,                # Deveria ser R$ 1.0K
        15000000,            # Deveria ser R$ 15.0M
    ]
    
    print(f"{'Valor':<20} {'Dashboard':<15} {'Simples':<15} {'Igual?':<10}")
    print("=" * 60)
    
    for val in valores_teste:
        resultado_dashboard = formatar_valor_curto_dashboard(val)
        resultado_simples = formatar_valor_curto_simples(val)
        igual = "✅" if resultado_dashboard == resultado_simples else "❌"
        
        print(f"{val:<20.2f} {resultado_dashboard:<15} {resultado_simples:<15} {igual:<10}")
    
    print("\n🎯 Análise Específica:")
    print("Valores que deveriam aparecer no dashboard:")
    
    testes_especificos = [
        (15589793.17126484, "R$ 15.6M"),
        (9550752.759616392, "R$ 9.6M"),
        (183600000.0, "R$ 183.6M"),
        (694000000.0, "R$ 694.0M"),
    ]
    
    for val, esperado in testes_especificos:
        resultado = formatar_valor_curto_dashboard(val)
        status = "✅" if resultado == esperado else "❌"
        print(f"  {val:>15.2f} -> {resultado:<15} (esperado: {esperado:<10}) {status}")
    
    print("\n🔍 Teste da substituição de caracteres:")
    valor_teste = 15589793.17126484
    print(f"Valor original: {valor_teste}")
    
    # Passo a passo da formatação complexa
    v = float(valor_teste)
    if v >= 1_000:
        resultado_formatado = f"R$ {v / 1_000:,.1f}M".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"Resultado: {resultado_formatado}")
        print(f"Passos:")
        print(f"  1. R$ {v / 1_000:,.1f}M = R$ {v / 1_000:,.1f}M")
        print(f"  2. .replace(',', 'X') = R$ {v / 1_000:,.1f}M.replace(',', 'X')}")
        print(f"  3. .replace('.', ',') = R$ {v / 1_000:,.1f}M.replace(',', 'X').replace('.', ',')}")
        print(f"  4. .replace('X', '.') = {resultado_formatado}")

if __name__ == "__main__":
    main()
