import pandas as pd
import sqlite3

def adicionar_coluna_feebased():
    """
    Adiciona coluna "FeeBased" ao arquivo Assessores_PL_Enriquecido.xlsx
    usando dados do arquivo DBV Capital_FeeBased.xlsx
    """
    
    print("🔄 Adicionando coluna FeeBased...")
    
    try:
        # 1. Ler o arquivo enriquecido
        print("📖 Lendo arquivo Assessores_PL_Enriquecido.xlsx...")
        df_enriquecido = pd.read_excel("Assessores_PL_Enriquecido.xlsx")
        print(f"   - {len(df_enriquecido)} assessores encontrados")
        
        # 2. Ler o arquivo FeeBased Excel
        print("📖 Lendo arquivo DBV Capital_FeeBased.xlsx...")
        df_feebased = pd.read_excel("DBV Capital_FeeBased.xlsx")
        print(f"   - {len(df_feebased)} registros encontrados")
        print(f"   - Colunas: {list(df_feebased.columns)}")
        
        # 3. Verificar as colunas do FeeBased
        print("\n📋 Estrutura do arquivo FeeBased:")
        print(df_feebased.head(3))
        print(f"\n📋 Tipos de dados:")
        print(df_feebased.dtypes)
        
        # 4. Identificar colunas relevantes
        # Procurar por colunas de código do assessor e P/L
        colunas_assessor = [col for col in df_feebased.columns if 'código' in col.lower() or 'assessor' in col.lower() or 'cod' in col.lower()]
        colunas_pl = [col for col in df_feebased.columns if 'p/l' in col.lower() or 'pl' in col.lower() or 'patrim' in col.lower()]
        colunas_status = [col for col in df_feebased.columns if 'status' in col.lower() or 'situação' in col.lower()]
        
        print(f"\n🎯 Colunas encontradas:")
        print(f"   - Assessor: {colunas_assessor}")
        print(f"   - P/L: {colunas_pl}")
        print(f"   - Status: {colunas_status}")
        
        if not colunas_assessor or not colunas_pl:
            print("❌ Colunas essenciais não encontradas no arquivo FeeBased")
            return None
        
        # Usar as colunas corretas
        col_assessor = 'Código Assessor'
        col_pl = 'P/L'
        col_status = 'Status'
        
        print(f"\n📊 Usando colunas:")
        print(f"   - Código Assessor: {col_assessor}")
        print(f"   - P/L: {col_pl}")
        print(f"   - Status: {col_status}")
        
        # 5. Filtrar apenas registros ativos
        if col_status:
            print(f"\n🔍 Filtrando registros ativos...")
            # Verificar valores únicos na coluna de status
            valores_status = df_feebased[col_status].unique()
            print(f"   - Valores de status encontrados: {valores_status}")
            
            # Filtrar por diferentes variações de "ativo"
            status_ativo = ['ativo', 'ATIVO', 'Ativo', 'A', 'a']
            df_feebased_filtrado = df_feebased[df_feebased[col_status].isin(status_ativo)]
            print(f"   - Registros ativos: {len(df_feebased_filtrado)}")
        else:
            print("   - Sem coluna de status, usando todos os registros")
            df_feebased_filtrado = df_feebased.copy()
        
        # 6. Converter P/L para numérico
        df_feebased_filtrado['pl_numeric'] = pd.to_numeric(df_feebased_filtrado[col_pl], errors='coerce').fillna(0)
        
        # 7. Agrupar por assessor e somar P/L
        print("\n💰 Calculando P/L FeeBased por assessor...")
        pl_feebased_por_assessor = df_feebased_filtrado.groupby(col_assessor)['pl_numeric'].sum().reset_index()
        pl_feebased_por_assessor.columns = ['codigo_assessor', 'FeeBased']
        
        print(f"   - {len(pl_feebased_por_assessor)} assessores com FeeBased")
        
        # 8. Adicionar coluna ao arquivo enriquecido
        print("\n🔗 Adicionando coluna FeeBased ao arquivo enriquecido...")
        
        # Garantir que os códigos estejam no mesmo formato
        # Adicionar prefixo "A" aos códigos do arquivo enriquecido
        df_enriquecido['codigo_pad'] = 'A' + df_enriquecido['CÓDIGO ASSESSOR'].astype(str).str.strip()
        pl_feebased_por_assessor['codigo_pad'] = pl_feebased_por_assessor['codigo_assessor'].astype(str).str.strip()
        
        # Fazer o merge
        df_final = df_enriquecido.merge(
            pl_feebased_por_assessor[['codigo_pad', 'FeeBased']], 
            left_on='codigo_pad', 
            right_on='codigo_pad', 
            how='left'
        )
        
        # Preencher valores nulos com 0
        df_final['FeeBased'] = df_final['FeeBased'].fillna(0)
        
        # Remover coluna temporária
        df_final = df_final.drop('codigo_pad', axis=1)
        
        # 9. Salvar arquivo final
        print("\n💾 Salvando arquivo final...")
        nome_arquivo_final = "Assessores_PL_Completo.xlsx"
        
        with pd.ExcelWriter(nome_arquivo_final, engine='openpyxl') as writer:
            df_final.to_excel(writer, sheet_name='Assessores_Completos', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Assessores_Completos']
            for idx, col in enumerate(df_final.columns):
                max_length = max(
                    df_final[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Arquivo salvo: {nome_arquivo_final}")
        
        # 10. Resumo estatístico
        print("\n📊 Resumo FeeBased:")
        assessores_com_feebased = (df_final['FeeBased'] > 0).sum()
        total_feebased = df_final['FeeBased'].sum()
        
        print(f"   - Assessores com FeeBased: {assessores_com_feebased} de {len(df_final)}")
        print(f"   - Total FeeBased: R$ {total_feebased:,.2f}")
        print(f"   - Média FeeBased por assessor: R$ {df_final['FeeBased'].mean():,.2f}")
        
        print(f"\n📋 Top 5 assessores por FeeBased:")
        top_feebased = df_final.nlargest(5, 'FeeBased')[['CÓDIGO ASSESSOR', 'NOME ASSESSOR', 'FeeBased']]
        print(top_feebased.to_string(index=False))
        
        return nome_arquivo_final
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    adicionar_coluna_feebased()
