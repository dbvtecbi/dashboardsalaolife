"""
Mapeamento de colunas entre o código e o banco de dados.
"""

COLUMN_MAPPING = {
    # Mapeamento de nomes de colunas esperados para nomes reais
    'capital_positivador': 'Relatório Positivador',
    'Data_Posicao': 'Data_Posição',
    'Captacao_Liquida_em_M': 'Captação_Líquida_em_M',
    'Net_em_M': 'Net_Em_M',
    'Data_Atualizacao': 'Data_Atualização',
    'Aplicacao_Financeira_Declarada_Ajustada': 'Aplicação_Financeira_Declarada_Ajustada',
    'Receita_no_Mes': 'Receita_no_Mês',
    'Receita_Aluguel': 'Receita_Aluguel',
    'Receita_Complemento_Pacote_Corretagem': 'Receita_Complemento_Pacote_Corretagem',
    'Tipo_Pessoa': 'Tipo_Pessoa',
    'Assessor': 'Assessor',
    'Cliente': 'Cliente'
}

def get_column_mapping(expected_column):
    """Retorna o nome real da coluna com base no nome esperado.
    
    Args:
        expected_column (str): Nome da coluna esperado no código.
        
    Returns:
        str or dict: Se expected_column for 'all', retorna o dicionário completo.
                    Caso contrário, retorna o nome mapeado da coluna ou o próprio nome se não existir mapeamento.
    """
    if expected_column == 'all':
        return COLUMN_MAPPING
    return COLUMN_MAPPING.get(expected_column, expected_column)

def get_table_name(expected_table):
    """Retorna o nome real da tabela com base no nome esperado."""
    return COLUMN_MAPPING.get(expected_table, expected_table)
