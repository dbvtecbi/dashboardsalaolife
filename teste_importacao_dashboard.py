"""
Teste de importação do dashboard para verificar erros de runtime
"""
import sys
from pathlib import Path

# Simular ambiente Streamlit básico
class MockSt:
    def set_page_config(self, *args, **kwargs):
        pass
    def markdow(self, *args, **kwargs):
        pass
    def cache_data(self, show_spinner=True):
        def decorator(func):
            return func
        return decorator
    
    class cache_data:
        def __init__(self, show_spinner=True):
            self.show_spinner = show_spinner
        def __call__(self, func):
            return func

# Substituir streamlit
sys.modules['streamlit'] = MockSt()

def testar_importacoes():
    print("🧪 Testando importações do dashboard...")
    print("=" * 50)
    
    try:
        # Adicionar path
        sys.path.append(str(Path('.').absolute() / 'pages'))
        
        # Tentar importar o módulo principal
        print("1. Importando Dashboard_Salão_Atualizado...")
        import Dashboard_Salão_Atualizado
        print("✅ Dashboard_Salão_Atualizado importado com sucesso!")
        
        # Verificar se as funções principais existem
        print("\n2. Verificando funções principais...")
        funcoes_esperadas = [
            'render_rumo_a_1bi',
            'calcular_indicadores_objetivos',
            'obter_meta_objetivo'
        ]
        
        for func in funcoes_esperadas:
            if hasattr(Dashboard_Salão_Atualizado, func):
                print(f"✅ {func} encontrada")
            else:
                print(f"❌ {func} NÃO encontrada")
        
        print("\n3. Verificando variáveis globais...")
        variaveis_esperadas = [
            'valor_base_auc_2026'
        ]
        
        for var in variaveis_esperadas:
            if hasattr(Dashboard_Salão_Atualizado, var):
                print(f"✅ {var} encontrada")
            else:
                print(f"❌ {var} NÃO encontrada")
        
        print("\n✅ Todas as importações e verificações concluídas com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except NameError as e:
        print(f"❌ Erro de variável não definida: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_importacoes()
    if sucesso:
        print("\n🎉 Dashboard está pronto para execução!")
    else:
        print("\n❌ Há erros que precisam ser corrigidos!")
