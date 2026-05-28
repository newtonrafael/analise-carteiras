import pandas as pd
from src.utils import valor_exibicao, TEXTO_SEM_VINCULO


def formatar_6_digitos(coluna):
    # Padroes usados na base Protheus: codigos com 6 digitos.
    return coluna.astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.zfill(6).replace('000nan', pd.NA)


def formatar_2_digitos(coluna):
    # Padroes usados na base Protheus: loja com 2 digitos.
    return coluna.astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.zfill(2).replace('00nan', pd.NA)


def carregar_dados(caminho_base='data/base.csv', caminho_nomes='data/mata030.csv'):
    base = pd.read_csv(caminho_base, encoding='latin-1', sep=',', skiprows=2)
    nomes = pd.read_csv(caminho_nomes, encoding='latin-1', sep=',', skiprows=6)

    # Remove espacos vindos do cabecalho dos CSVs para estabilizar os nomes das colunas.
    base.columns = base.columns.str.strip()
    nomes.columns = nomes.columns.str.strip()

    colunas_6 = ['Codigo', 'Vendedor', 'Repres. Ext.', 'Vendedor Coo', 'Gerente Vend']
    for col in colunas_6:
        if col in base.columns:
            base[col] = formatar_6_digitos(base[col])
        if col in nomes.columns:
            nomes[col] = formatar_6_digitos(nomes[col])

    if 'Loja' in base.columns:
        base['Loja'] = formatar_2_digitos(base['Loja'])

    # CodLoja passa a ser a chave curta usada nas consultas por cliente/filial.
    base['CodLoja'] = (
        base['Codigo'].fillna('').astype(str).str.strip() +
        base['Loja'].fillna('').astype(str).str.strip()
    ).str.upper()

    # Traduz os codigos de colaboradores para "codigo - nome" usando a mata030.
    guia_nomes = dict(zip(nomes['Codigo'], nomes['Codigo'] + ' - ' + nomes['Nome']))

    # Preserva o vendedor cru para as analises de "gestor sem vendedor interno".
    base['Vendedor_Original'] = base['Vendedor']

    base['Vendedor'] = base['Vendedor'].map(guia_nomes)
    base['Repres. Ext.'] = base['Repres. Ext.'].map(guia_nomes)
    base['Vendedor Coo'] = base['Vendedor Coo'].map(guia_nomes)
    base['Gerente Vend'] = base['Gerente Vend'].map(guia_nomes)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    return base


def montar_tabela_clientes(df):
    # Monta a grade mais completa da carteira, com cliente + toda a equipe comercial.
    codigo = df['Codigo'].fillna('').astype(str).str.strip() if 'Codigo' in df.columns else pd.Series([''] * len(df), index=df.index)
    loja = df['Loja'].fillna('').astype(str).str.strip() if 'Loja' in df.columns else pd.Series([''] * len(df), index=df.index)

    tabela = pd.DataFrame(index=df.index)
    tabela['CodLoja'] = (codigo + loja).str[:8]
    tabela['Nome'] = df['Nome'].apply(lambda x: valor_exibicao(x, 'NOME NAO INFORMADO')) if 'Nome' in df.columns else 'NOME NAO INFORMADO'
    tabela['Vendedor'] = df['Vendedor'].apply(valor_exibicao) if 'Vendedor' in df.columns else TEXTO_SEM_VINCULO
    tabela['Gestor'] = df['Vendedor Coo'].apply(valor_exibicao) if 'Vendedor Coo' in df.columns else TEXTO_SEM_VINCULO
    tabela['Representante'] = df['Repres. Ext.'].apply(valor_exibicao) if 'Repres. Ext.' in df.columns else TEXTO_SEM_VINCULO
    tabela['Gerente'] = df['Gerente Vend'].apply(valor_exibicao) if 'Gerente Vend' in df.columns else TEXTO_SEM_VINCULO

    for coluna, largura in [('Nome', 32), ('Vendedor', 28), ('Gestor', 28), ('Representante', 28), ('Gerente', 28)]:
        tabela[coluna] = tabela[coluna].astype(str).str[:largura]

    return tabela


def montar_tabela_equipe(df, limitar_texto=True):
    # Versao resumida usada nas consultas por cliente e nos detalhamentos do menu.
    codigo = df['Codigo'].fillna('').astype(str).str.strip() if 'Codigo' in df.columns else pd.Series([''] * len(df), index=df.index)
    loja = df['Loja'].fillna('').astype(str).str.strip() if 'Loja' in df.columns else pd.Series([''] * len(df), index=df.index)

    tabela = pd.DataFrame(index=df.index)
    tabela['CodLoja'] = (codigo + loja).str[:8]
    tabela['Vendedor'] = df['Vendedor'].apply(valor_exibicao) if 'Vendedor' in df.columns else TEXTO_SEM_VINCULO
    tabela['Gestor'] = df['Vendedor Coo'].apply(valor_exibicao) if 'Vendedor Coo' in df.columns else TEXTO_SEM_VINCULO
    tabela['Representante'] = df['Repres. Ext.'].apply(valor_exibicao) if 'Repres. Ext.' in df.columns else TEXTO_SEM_VINCULO
    tabela['Gerven'] = df['Gerente Vend'].apply(valor_exibicao) if 'Gerente Vend' in df.columns else TEXTO_SEM_VINCULO

    if limitar_texto:
        for coluna, largura in [('Vendedor', 28), ('Gestor', 28), ('Representante', 28), ('Gerven', 28)]:
            tabela[coluna] = tabela[coluna].astype(str).str[:largura]

    return tabela
