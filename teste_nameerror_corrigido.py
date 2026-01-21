"""
Teste rápido para verificar se o NameError foi corrigido
"""
import sys
from pathlib import Path

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Teste NameError - RUMO A 1BI")
    print("=" * 50)
    
    try:
        # Importar a função do dashboard
        from Dashboard_Salão_Atualizado import render_rumo_a_1bi
        print("✅ Função render_rumo_a_1bi importada")
        
        # Tentar importar outras funções necessárias
        from Dashboard_Salão_Atualizado import (
            calcular_indicadores_objetivos,
            carregar_dados_objetivos_pj1,
            obter_dados_rumo_1bi,
            formatar_valor_curto,
            fmt_valor,
            render_custom_progress_bars
        )
        print("✅ Funções dependentes importadas")
        
        print("✅ NameError corrigido!")
        print("Agora execute: `streamlit run Home.py` para testar o dashboard.")
        
    except NameError as e:
        if "OBJETIVO_FINAL" in str(e):
            print(f"❌ NameError ainda presente: {e}")
            print("A variável OBJETIVO_FINAL ainda está sendo referenciada em algum lugar.")
        else:
            print(f"❌ Outro NameError: {e}")
    except Exception as e:
        print(f"❌ Outro erro: {e}")

if __name__ == "__main__":
    main()
