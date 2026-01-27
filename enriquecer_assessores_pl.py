import pandas as pd
import sqlite3
import numpy as np

def enriquecer_assessores_pl():
    """
    Adiciona colunas ao arquivo Assessores_PL.xlsx com dados extraídos dos bancos
    """
    
    print("🔄 Enriquecendo arquivo Assessores_PL.xlsx...")
    
    try:
        # 1. Ler o arquivo base
        print("📖 Lendo arquivo Assessores_PL.xlsx...")
        df_assessores = pd.read_excel("Assessores_PL.xlsx")
        print(f"   - {len(df_assessores)} assessores encontrados")
        print(f"   - Colunas: {list(df_assessores.columns)}")
        
        # 2. Conectar ao banco Positivador MTD
        print("📊 Conectando ao DBV Capital_Positivador (MTD).db...")
        conn_positivador = sqlite3.connect("DBV Capital_Positivador (MTD).db")
        
        # Ler dados do positivador
        query_positivador = """
        SELECT 
            Assessor,
            Cliente,
            "Net Em M" as net_em_m,
            "Aplicação Financeira Declarada Ajustada" as aplicacao_declarada,
            "Captação Líquida em M" as captacao_liquida
        FROM positivador_mtd
        WHERE Assessor IS NOT NULL AND Assessor != ''
        """
        
        df_positivador = pd.read_sql_query(query_positivador, conn_positivador)
        conn_positivador.close()
        
        print(f"   - {len(df_positivador)} registros lidos do positivador")
        
        # 3. Conectar ao banco FeeBased
        print("📊 Conectando ao DBV Capital_FeeBased.db...")
        conn_feebased = sqlite3.connect("DBV Capital_FeeBased.db")
        
        # Ler dados do feebased
        query_feebased = """
        SELECT 
            "código assessor" as codigo_assessor,
            "P/L" as pl_feebased,
            status
        FROM feebased
        WHERE "código assessor" IS NOT NULL 
        AND "código assessor" != ''
        AND status = 'ativo'
        """
        
        df_feebased = pd.read_sql_query(query_feebased, conn_feebased)
        conn_feebased.close()
        
        print(f"   - {len(df_feebased)} registros ativos lidos do feebased")
        
        # 4. Processar dados
        
        # Converter colunas para numérico
        df_positivador['net_em_m'] = pd.to_numeric(df_positivador['net_em_m'], errors='coerce').fillna(0)
        df_positivador['aplicacao_declarada'] = pd.to_numeric(df_positivador['aplicacao_declarada'], errors='coerce').fillna(0)
        df_positivador['captacao_liquida'] = pd.to_numeric(df_positivador['captacao_liquida'], errors='coerce').fillna(0)
        df_feebased['pl_feebased'] = pd.to_numeric(df_feebased['pl_feebased'], errors='coerce').fillna(0)
        
        # 4.1 Calcular QTD Clientes Únicos por assessor
        print("🔢 Calculando QTD Clientes Únicos...")
        clientes_unicos = df_positivador.groupby('Assessor')['Cliente'].nunique().reset_index()
        clientes_unicos.columns = ['Assessor', 'QTD_Clientes']
        
        # 4.2 Calcular PL total por assessor
        print("💰 Calculando PL total por assessor...")
        pl_total = df_positivador.groupby('Assessor')['net_em_m'].sum().reset_index()
        pl_total.columns = ['Assessor', 'PL_Total']
        
        # 4.3 Calcular Aplicação Declarada total por assessor
        print("📈 Calculando Aplicação Declarada por assessor...")
        aplicacao_total = df_positivador.groupby('Assessor')['aplicacao_declarada'].sum().reset_index()
        aplicacao_total.columns = ['Assessor', 'Aplicacao_Total']
        
        # 4.4 Calcular Captação Líquida por assessor
        print("📊 Calculando Captação Líquida por assessor...")
        captacao_total = df_positivador.groupby('Assessor')['captacao_liquida'].sum().reset_index()
        captacao_total.columns = ['Assessor', 'Captacao_Total']
        
        # 4.5 Calcular PL FeeBased por assessor
        print("💼 Calculando PL FeeBased por assessor...")
        pl_feebased_total = df_feebased.groupby('codigo_assessor')['pl_feebased'].sum().reset_index()
        pl_feebased_total.columns = ['Assessor', 'PL_FeeBased']
        
        # 5. Juntar todos os dados
        print("🔗 Juntando todos os dados...")
        
        # Merge com dados base
        df_enriquecido = df_assessores.copy()
        
        # Garantir que os códigos dos assessores estejam no mesmo formato
        df_enriquecido['Assessor_pad'] = df_enriquecido['CÓDIGO ASSESSOR'].astype(str).str.strip()
        clientes_unicos['Assessor_pad'] = clientes_unicos['Assessor'].astype(str).str.strip()
        pl_total['Assessor_pad'] = pl_total['Assessor'].astype(str).str.strip()
        aplicacao_total['Assessor_pad'] = aplicacao_total['Assessor'].astype(str).str.strip()
        captacao_total['Assessor_pad'] = captacao_total['Assessor'].astype(str).str.strip()
        pl_feebased_total['Assessor_pad'] = pl_feebased_total['Assessor'].astype(str).str.strip()
        
        # Fazer os merges
        df_enriquecido = df_enriquecido.merge(clientes_unicos[['Assessor_pad', 'QTD_Clientes']], 
                                            left_on='Assessor_pad', right_on='Assessor_pad', how='left')
        df_enriquecido = df_enriquecido.merge(pl_total[['Assessor_pad', 'PL_Total']], 
                                            left_on='Assessor_pad', right_on='Assessor_pad', how='left')
        df_enriquecido = df_enriquecido.merge(aplicacao_total[['Assessor_pad', 'Aplicacao_Total']], 
                                            left_on='Assessor_pad', right_on='Assessor_pad', how='left')
        df_enriquecido = df_enriquecido.merge(captacao_total[['Assessor_pad', 'Captacao_Total']], 
                                            left_on='Assessor_pad', right_on='Assessor_pad', how='left')
        df_enriquecido = df_enriquecido.merge(pl_feebased_total[['Assessor_pad', 'PL_FeeBased']], 
                                            left_on='Assessor_pad', right_on='Assessor_pad', how='left')
        
        # 6. Calcular as colunas solicitadas
        
        # Ticket Médio = PL Total / QTD Clientes
        df_enriquecido['Ticket Médio'] = np.where(
            df_enriquecido['QTD_Clientes'] > 0,
            df_enriquecido['PL_Total'] / df_enriquecido['QTD_Clientes'],
            0
        )
        
        # % Share of Wallet = PL Total / Aplicação Declarada
        df_enriquecido['% Share of Wallet'] = np.where(
            df_enriquecido['Aplicacao_Total'] > 0,
            (df_enriquecido['PL_Total'] / df_enriquecido['Aplicacao_Total']) * 100,
            0
        )
        
        # Aderência FeeBased = PL FeeBased
        df_enriquecido['Aderencia FeeBased'] = df_enriquecido['PL_FeeBased'].fillna(0)
        
        # Captação = Captação Total
        df_enriquecido['Captação'] = df_enriquecido['Captacao_Total'].fillna(0)
        
        # 7. Formatar colunas
        print("🎨 Formatando colunas...")
        
        # Preencher valores nulos
        df_enriquecido['QTD_Clientes'] = df_enriquecido['QTD_Clientes'].fillna(0).astype(int)
        df_enriquecido['PL_Total'] = df_enriquecido['PL_Total'].fillna(0)
        df_enriquecido['Aplicacao_Total'] = df_enriquecido['Aplicacao_Total'].fillna(0)
        df_enriquecido['PL_FeeBased'] = df_enriquecido['PL_FeeBased'].fillna(0)
        df_enriquecido['Captacao_Total'] = df_enriquecido['Captacao_Total'].fillna(0)
        
        # 8. Salvar arquivo enriquecido
        print("💾 Salvando arquivo enriquecido...")
        
        nome_arquivo_saida = "Assessores_PL_Enriquecido.xlsx"
        
        with pd.ExcelWriter(nome_arquivo_saida, engine='openpyxl') as writer:
            df_enriquecido.to_excel(writer, sheet_name='Assessores_Enriquecidos', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Assessores_Enriquecidos']
            for idx, col in enumerate(df_enriquecido.columns):
                max_length = max(
                    df_enriquecido[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Arquivo salvo: {nome_arquivo_saida}")
        
        # 9. Resumo estatístico
        print("\n📊 Resumo estatístico:")
        print(f"   - Total assessores: {len(df_enriquecido)}")
        print(f"   - Assessores com clientes: {(df_enriquecido['QTD_Clientes'] > 0).sum()}")
        print(f"   - Ticket médio geral: R$ {df_enriquecido['Ticket Médio'].mean():,.2f}")
        print(f"   - Share of wallet médio: {df_enriquecido['% Share of Wallet'].mean():.2f}%")
        print(f"   - Total PL FeeBased: R$ {df_enriquecido['Aderencia FeeBased'].sum():,.2f}")
        print(f"   - Total Captação: R$ {df_enriquecido['Captação'].sum():,.2f}")
        
        print(f"\n📋 Top 5 assessores por Ticket Médio:")
        top_ticket = df_enriquecido.nlargest(5, 'Ticket Médio')[['CÓDIGO ASSESSOR', 'NOME ASSESSOR', 'QTD_Clientes', 'Ticket Médio']]
        print(top_ticket.to_string(index=False))
        
        return nome_arquivo_saida
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    enriquecer_assessores_pl()
