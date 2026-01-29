import sqlite3
import pandas as pd
from datetime import datetime

# Mapeamento de assessores (extraído do Dashboard_Salão_Life.py)
ASSESSORES_MAP = {
    "A92300": "Adil Amorim",
    "A95715": "André Norat", 
    "A87867": "Arthur Linhares",
    "A95796": "Artur Vaz",
    "A96676": "Artur Vaz",
    "A95642": "Bruna Lewis",
    "A26892": "Carlos Monteiro",
    "A71490": "Cesar Lima",
    "A93081": "Daniel Morone",
    "A23594": "Diego Monteiro",
    "A23454": "Eduardo Monteiro",
    "A91619": "Eduardo Parente",
    "A95635": "Enzo Rei",
    "A50825": "Fabiane Souza",
    "A46886": "Fábio Tomaz",
    "A96625": "Gustavo Levy",
    "A95717": "Henrique Vieira",
    "A94115": "Israel Oliveira Moraes",
    "A97328": "João Goldenberg ",
    "A41471": "João Georg de Andrade",
    "A69453": "Guilherme Peçanha",
    "A51586": "Luiz Eduardo Mesquita",
    "A28215": "Luiz Coimbra",
    "A92301": "Marcus Faria",
    "A38061": "Paulo Pinho",
    "A69265": "Paulo Gomes",
    "A72213": "Thiago Cordeiro",
    "A26914": "Victor Garrido",
}

# Mapeamento de áreas (extraído do Dashboard_Salão_Life.py)
AREA_MAP = {
    "Vida": ["Vida", "Seguros", "Seguro", "Vida/Seguros", "Vida e Seguros"],
    "Auto/RE": ["Auto/RE", "AutoRE", "Auto", "RE"],
    "Saúde": ["Saúde", "Saude"],
    "Câmbio": ["Câmbio", "Cambio"],
    "Consórcio": ["Consórcio", "Consorcio"],
    "Crédito": ["Crédito", "Credito"],
}

def normalizar_texto(texto):
    """Normaliza texto para comparação (remove acentos e converte para minúsculas)"""
    import unicodedata
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.lower().strip()

def obter_nome_assessor(codigo):
    """Obtém nome do assessor pelo código"""
    codigo_str = str(codigo) if codigo is not None else ""
    return ASSESSORES_MAP.get(codigo_str, f"Não encontrado ({codigo_str})")

def gerar_excel_areas_assessores():
    """Gera Excel com valores de assessores por área"""
    
    print("🔍 Gerando Excel de Assessores por Área...")
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('DBV Capital_Produtos.db')
        
        # Carregar todos os dados
        query = """
        SELECT 
            [Código Assessor] as codigo_assessor,
            [Linha Receita] as linha_receita,
            [Valor Negócio (R$)] as valor_negocio
        FROM Produtos 
        WHERE [Código Assessor] IS NOT NULL 
        AND [Código Assessor] != ''
        AND [Valor Negócio (R$)] IS NOT NULL
        AND [Valor Negócio (R$)] > 0
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"📊 Total de registros encontrados: {len(df)}")
        
        # Inicializar DataFrame para o resultado
        resultado_data = []
        
        # Para cada área definida no AREA_MAP
        for area_nome, area_valores in AREA_MAP.items():
            print(f"\n🏢 Processando área: {area_nome}")
            
            # Normalizar valores de busca para esta área
            valores_normalizados = [normalizar_texto(v) for v in area_valores]
            
            # Filtrar dados para esta área
            df_area = df[df['linha_receita'].apply(lambda x: normalizar_texto(x) in valores_normalizados)]
            
            print(f"   📊 Registros encontrados: {len(df_area)}")
            
            # Agrupar por assessor
            assessores_area = df_area.groupby('codigo_assessor')['valor_negocio'].sum().reset_index()
            
            # Adicionar nome do assessor
            assessores_area['nome_assessor'] = assessores_area['codigo_assessor'].apply(lambda x: obter_nome_assessor(x))
            
            # Ordenar por valor (maior para menor)
            assessores_area = assessores_area.sort_values('valor_negocio', ascending=False)
            
            # Adicionar ao resultado
            for _, row in assessores_area.iterrows():
                try:
                    resultado_data.append({
                        'Área': area_nome,
                        'Código Assessor': str(row['codigo_assessor']),
                        'Nome Assessor': str(row['nome_assessor']),
                        'Valor Total': float(row['valor_negocio'])
                    })
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar linha: {e}")
                    print(f"   📊 Dados da linha: {row.to_dict()}")
        
        # Criar DataFrame final
        df_resultado = pd.DataFrame(resultado_data)
        
        # Criar tabela pivô (uma coluna para cada área)
        df_pivot = df_resultado.pivot_table(
            index=['Código Assessor', 'Nome Assessor'],
            columns='Área',
            values='Valor Total',
            fill_value=0
        ).reset_index()
        
        # Reordenar colunas
        colunas_area = list(AREA_MAP.keys())
        df_pivot = df_pivot[['Código Assessor', 'Nome Assessor'] + colunas_area]
        
        # Adicionar coluna de total geral
        df_pivot['Total Geral'] = df_pivot[colunas_area].sum(axis=1)
        
        # Ordenar por total geral (maior para menor)
        df_pivot = df_pivot.sort_values('Total Geral', ascending=False)
        
        # Gerar arquivo Excel
        nome_arquivo = f"Assessores_por_Area_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            # Planilha 1: Tabela pivô (uma coluna por área)
            df_pivot.to_excel(writer, sheet_name='Resumo por Área', index=False)
            
            # Planilha 2: Dados detalhados
            df_resultado.to_excel(writer, sheet_name='Dados Detalhados', index=False)
            
            # Ajustar largura das colunas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"\n✅ Excel gerado com sucesso: {nome_arquivo}")
        print(f"📊 Total de assessores únicos: {len(df_pivot)}")
        print(f"📊 Valor total geral: R$ {df_pivot['Total Geral'].sum():,.2f}")
        
        # Mostrar resumo por área
        print(f"\n📈 Resumo por Área:")
        for area in colunas_area:
            total_area = df_pivot[area].sum()
            if total_area > 0:
                print(f"   - {area}: R$ {total_area:,.2f}")
        
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    gerar_excel_areas_assessores()
