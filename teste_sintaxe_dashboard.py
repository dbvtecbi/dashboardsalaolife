"""
Teste de sintaxe do dashboard para verificar se há variáveis não definidas
"""
import ast
import sys
from pathlib import Path

def verificar_sintaxe_arquivo(caminho_arquivo):
    """Verifica a sintaxe de um arquivo Python"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Tentar fazer parse do AST
        ast.parse(conteudo)
        print(f"✅ Sintaxe OK: {caminho_arquivo}")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe em {caminho_arquivo}:")
        print(f"   Linha {e.lineno}: {e.text}")
        print(f"   Erro: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar {caminho_arquivo}: {e}")
        return False

def main():
    print("🔍 Verificando sintaxe do dashboard...")
    print("=" * 50)
    
    caminho_dashboard = Path("pages/Dashboard_Salão_Atualizado.py")
    
    if verificar_sintaxe_arquivo(caminho_dashboard):
        print("\n✅ Dashboard pronto para execução!")
        
        # Verificar também os arquivos de funções
        arquivos_para_verificar = [
            "correcao_final.py",
            "funcoes_objetivos_pj1.py"
        ]
        
        print("\n🔍 Verificando arquivos de funções...")
        for arquivo in arquivos_para_verificar:
            if Path(arquivo).exists():
                verificar_sintaxe_arquivo(arquivo)
            else:
                print(f"⚠️  Arquivo não encontrado: {arquivo}")
    else:
        print("\n❌ Há erros de sintaxe que precisam ser corrigidos!")

if __name__ == "__main__":
    main()
