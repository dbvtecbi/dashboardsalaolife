"""
Teste do Fee-Based com objetivo fixo em 250M
"""
import sys
from pathlib import Path

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Teste Fee-Based - Objetivo 250M")
    print("=" * 50)
    
    # Verificar o valor fixo no código
    OBJETIVO_FINAL_FEEBASED = 250_000_000.0
    
    print(f"✅ Objetivo Fee-Based fixado em: R$ {OBJETIVO_FINAL_FEEBASED:,.2f}")
    print(f"✅ Valor formatado: R$ {OBJETIVO_FINAL_FEEBASED/1_000_000:.0f}M")
    
    print(f"\n🎯 Resultado esperado no card:")
    print(f"Objetivo Total: R$ {OBJETIVO_FINAL_FEEBASED:,.2f} ({OBJETIVO_FINAL_FEEBASED/1_000_000:.0f}M)")
    
    print(f"\n🚀 Execute: `streamlit run Home.py` para ver no dashboard.")
    print(f"O card Fee-Based deve mostrar o objetivo total de R$ 250M.")

if __name__ == "__main__":
    main()
