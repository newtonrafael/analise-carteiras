import os
from datetime import datetime

import pandas as pd
from openpyxl.utils import get_column_letter


def exportar_analise_vendedores_excel(resumo_vendedores, detalhe_gerentes_vendedor, tabela_clientes):
    # Gera um arquivo de apoio com tres abas: resumo, detalhamento e clientes.
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho_arquivo = os.path.abspath(f"output/analise_carteiras_vendedores_{timestamp}.xlsx")

    os.makedirs('output', exist_ok=True)

    resumo_excel = resumo_vendedores.copy()
    detalhe_excel = detalhe_gerentes_vendedor.rename(columns={'Gerente_Exibicao': 'Gerente'}).copy()
    clientes_excel = tabela_clientes.copy()

    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        resumo_excel.to_excel(writer, sheet_name='Resumo_Vendedores', index=False)
        detalhe_excel.to_excel(writer, sheet_name='Gerentes_por_Vendedor', index=False)
        clientes_excel.to_excel(writer, sheet_name='Clientes', index=False)

        for nome_planilha, df_planilha in {
            'Resumo_Vendedores': resumo_excel,
            'Gerentes_por_Vendedor': detalhe_excel,
            'Clientes': clientes_excel
        }.items():
            worksheet = writer.sheets[nome_planilha]
            worksheet.freeze_panes = 'A2'

            for indice_coluna, coluna in enumerate(df_planilha.columns, start=1):
                serie = df_planilha[coluna].fillna('').astype(str)
                maior_valor = serie.map(len).max() if not serie.empty else 0
                largura = min(max(len(coluna), maior_valor) + 2, 45)
                worksheet.column_dimensions[get_column_letter(indice_coluna)].width = largura

    return caminho_arquivo
