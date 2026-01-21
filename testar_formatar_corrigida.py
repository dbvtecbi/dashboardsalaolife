"""
Testar a função formatar_valor_curto corrigida
"""
import sys
from pathlib import Path

# Adicionar path
sys.path.append(str(Path('.').absolute() / 'pages'))

# Importar a função corrigida do dashboard
exec(open('pages/Dashboard_Salão_Atualizado.py').read().split('def fmt_valor_simples')[0])

def main():
    print("🔍 Teste da Função formatar_valor_curto CORRIGIDA")
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
        resultado = formatar_valor_curto(valor)
        if resultado != esperado:
            problemas.append(f"❌ {valor} -> {resultado} (esperado: {esperado})")
        else:
            print(f"✅ {valor} -> {resultado}")
    
    if problemas:
        print("\n⚠️ PROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(p)
    else:
        print("\n✅ Todos os testes passaram! A função foi corrigida com sucesso!")

if __name__ == "__main__":
    main()
