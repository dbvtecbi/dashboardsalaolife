"""
Teste simplificado da função formatar_valor_curto
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

def main():
    print("🔍 Teste da Função formatar_valor_curto do Dashboard")
    print("=" * 60)
    
    # Valores críticos
    testes = [
        (15589793.17126484, "R$ 15.6M"),
        (9550752.759616392, "R$ 9.6M"),
        (183600000.0, "R$ 183.6M"),
        (694000000.0, "R$ 694.0M"),
        (0, "R$ 0"),
        (1, "R$ 1"),
    ]
    
    problemas = []
    
    for valor, esperado in testes:
        resultado = formatar_valor_curto_dashboard(valor)
        if resultado != esperado:
            problemas.append(f"❌ {valor} -> {resultado} (esperado: {esperado})")
        else:
            print(f"✅ {valor} -> {resultado}")
    
    if problemas:
        print("\n⚠️ PROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(p)
    else:
        print("\n✅ Todos os testes passaram!")
    
    # Teste específico da substituição
    print("\n🔍 Teste da substituição de caracteres:")
    valor = 15589793.17126484
    v = float(valor)
    
    if v >= 1_000:
        passo1 = f"R$ {v / 1_000:,.1f}M"
        passo2 = passo1.replace(",", "X")
        passo3 = passo2.replace(".", ",")
        passo4 = passo3.replace("X", ".")
        resultado_final = passo4
        
        print(f"Valor: {valor}")
        print(f"Passo 1: {passo1}")
        print(f"Passo 2: {passo2}")
        print(f"Passo 3: {passo3}")
        print(f"Passo 4: {resultado_final}")
        print(f"Resultado esperado: R$ 15.6M")
        print(f"Igual: {'✅' if resultado_final == 'R$ 15.6M' else '❌'}")

if __name__ == "__main__":
    main()
