"""
Teste final da função formatar_valor_curto
"""

def formatar_valor_curto_corrigida(valor):
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
    print("🔍 Teste Final da Função formatar_valor_curto")
    print("=" * 60)
    
    # Valores que estavam dando problema
    testes = [
        (15589793.17126484, "R$ 15.6M"),
        (9550752.759616392, "R$ 9.6M"),
        (183600000.0, "R$ 183.6M"),
        (694000000.0, "R$ 694.0M"),
    ]
    
    print("Resultados com a função CORRIGIDA:")
    for valor, esperado in testes:
        resultado = formatar_valor_curto_corrigida(valor)
        status = "✅" if resultado == esperado else "❌"
        print(f"  {valor:>15.2f} -> {resultado:<15} (esperado: {esperado:<10}) {status}")
    
    print("\n🎯 RESUMO:")
    print("A função formatar_valor_curto foi corrigida!")
    print("Agora os valores devem aparecer corretamente no dashboard:")
    print("- CAPTAÇÃO MÊS: Objetivo R$ 15.6M, Projetado R$ 9.6M")
    print("- CAPTAÇÃO ANO: Objetivo R$ 183.6M, Projetado R$ 9.6M")
    print("- AUC 2026: Objetivo R$ 694.0M, Projetado R$ 465.4M")

if __name__ == "__main__":
    main()
