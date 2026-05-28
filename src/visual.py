import pandas as pd
from colorama import Fore, Style

from src.utils import (
    limpar_tela, desenhar_linha_topo, desenhar_linha_meio, desenhar_linha_baixo,
    print_centralizado, print_esquerda,
    print_linha_tabela_pendencias, print_linha_gerven_macro, print_linha_gestor_macro,
    print_linha_tabela_limpeza, print_linha_raio_x,
    contar_clientes_por_coluna, valor_exibicao, normalizar_codlojas,
    TEXTO_SEM_VINCULO
)
from src.tratamento import montar_tabela_clientes, montar_tabela_equipe
from src.exportacao import exportar_analise_vendedores_excel


# ---------------------------------------------------------------------
# OPÇÃO 1: PAINEL DE PENDÊNCIAS
# ---------------------------------------------------------------------
def menu_pendencias(base, colaboradores_ajustados):
    while True:
        limpar_tela()

        # Recalcula as carteiras pequenas a cada volta para refletir novos ajustes.
        dinamica_vendedor = base.groupby('Vendedor').agg(Qtd_Clientes=('Codigo', 'count'), Codigos_Alocados=('Codigo', lambda x: ', '.join(base.loc[x.index, 'Codigo'] + base.loc[x.index, 'Loja']))).reset_index()
        dinamica_vendedor = dinamica_vendedor[dinamica_vendedor['Qtd_Clientes'] < 30].sort_values(by='Qtd_Clientes', ascending=True)

        dinamica_repres = base.groupby('Repres. Ext.').agg(Qtd_Clientes=('Codigo', 'count'), Codigos_Alocados=('Codigo', lambda x: ', '.join(base.loc[x.index, 'Codigo'] + base.loc[x.index, 'Loja']))).reset_index()
        dinamica_repres = dinamica_repres[dinamica_repres['Qtd_Clientes'] < 30].sort_values(by='Qtd_Clientes', ascending=True)

        dinamica_coo = base.groupby('Vendedor Coo').agg(Qtd_Clientes=('Codigo', 'count'), Codigos_Alocados=('Codigo', lambda x: ', '.join(base.loc[x.index, 'Codigo'] + base.loc[x.index, 'Loja']))).reset_index()
        dinamica_coo = dinamica_coo[dinamica_coo['Qtd_Clientes'] < 30].sort_values(by='Qtd_Clientes', ascending=True)

        dinamica_gerente = base.groupby('Gerente Vend').agg(Qtd_Clientes=('Codigo', 'count'), Codigos_Alocados=('Codigo', lambda x: ', '.join(base.loc[x.index, 'Codigo'] + base.loc[x.index, 'Loja']))).reset_index()
        dinamica_gerente = dinamica_gerente[dinamica_gerente['Qtd_Clientes'] < 30].sort_values(by='Qtd_Clientes', ascending=True)

        # Estrutura unica para percorrer os quatro niveis da hierarquia comercial.
        tabelas_f1 = [
            (dinamica_vendedor, 'Vendedor', 'Vendedor Interno'),
            (dinamica_repres, 'Repres. Ext.', 'Representante'),
            (dinamica_coo, 'Vendedor Coo', 'Gestor'),
            (dinamica_gerente, 'Gerente Vend', 'Gerven')
        ]

        desenhar_linha_topo()
        print_centralizado("PAINEL DE PENDÊNCIAS (CARTEIRAS < 30 CLIENTES)", Fore.CYAN, Style.BRIGHT)

        tem_pendencia = False
        for df, col_nome, nome_visual in tabelas_f1:
            faltam = df[~df[col_nome].str.lower().isin(colaboradores_ajustados)]
            if not faltam.empty:
                tem_pendencia = True
                desenhar_linha_meio()
                print_centralizado(f"CAMPO: {nome_visual.upper()}", Fore.YELLOW, Style.BRIGHT)
                desenhar_linha_meio()
                print_linha_tabela_pendencias("COLABORADOR", "QTD CLIENTES")
                desenhar_linha_meio()

                for idx, row in faltam.iterrows():
                    print_linha_tabela_pendencias(row[col_nome], row['Qtd_Clientes'])

        if not tem_pendencia:
            desenhar_linha_meio()
            print_centralizado("🎉 PARABÉNS! Todos os erros da base foram corrigidos!", Fore.GREEN, Style.BRIGHT)
            desenhar_linha_baixo()
            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao menu...")
            break

        desenhar_linha_meio()
        print_centralizado("Digite '0' ou 'voltar' para sair deste painel.", Fore.GREEN)
        desenhar_linha_baixo()

        busca = input(Style.BRIGHT + "\n 🔍 Buscar Colaborador: ").strip().lower()
        if busca in ['0', 'voltar', 'sair']:
            break

        # Procura o colaborador em todos os papeis e guarda os detalhes da pendencia.
        ERROS_AQUI = {}
        for df, col_nome, nome_visual in tabelas_f1:
            achado = df[df[col_nome].str.contains(busca, case=False, na=False)]
            if not achado.empty:
                qtd = achado['Qtd_Clientes'].values[0]
                nome_completo = achado[col_nome].values[0]
                if qtd > 0 and (nome_completo.lower() not in colaboradores_ajustados):
                    ERROS_AQUI[nome_visual] = {'nome': nome_completo, 'qtd': qtd, 'codigos': achado['Codigos_Alocados'].values[0], 'col_origem': col_nome}

        if ERROS_AQUI:
            # Quando o mesmo nome aparece em mais de um papel, prioriza a menor carteira.
            visual_com_erro = min(ERROS_AQUI, key=lambda k: ERROS_AQUI[k]['qtd'])
            dados_erro = ERROS_AQUI[visual_com_erro]

            print("\n")
            desenhar_linha_topo()
            print_centralizado("RESULTADO DA ANÁLISE", Fore.YELLOW, Style.BRIGHT)
            desenhar_linha_meio()
            print_esquerda(f"Colaborador: {dados_erro['nome']}")
            print_esquerda(f"Campo no Protheus: {visual_com_erro}")
            print_esquerda(f"Quantidade Suspeita: {dados_erro['qtd']} clientes")
            desenhar_linha_meio()
            print_centralizado("📋 CÓDIGOS-LOJA PARA CORRIGIR NO PROTHEUS:", Fore.GREEN, Style.BRIGHT)
            desenhar_linha_meio()
            print_esquerda(dados_erro['codigos'])
            desenhar_linha_meio()
            confirmacao = input(Fore.YELLOW + Style.BRIGHT + " 👉 Já corrigiu este colaborador no Protheus? (S/N): ").strip().lower()
            if confirmacao in ['s', 'sim', 'y', 'yes']:
                colaboradores_ajustados.append(dados_erro['nome'].lower())
        else:
            print(Fore.RED + "\n ❌ Colaborador não encontrado ou sem pendências.")
            input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para continuar...")


# ---------------------------------------------------------------------
# OPÇÃO 2: ANALISE DE CARTEIRA POR GERENTE
# ---------------------------------------------------------------------
def menu_carteira_gerente(base):
    while True:
        limpar_tela()
        # Essa opcao abre pela visao do gerente e depois permite descer para vendedor.
        base_com_gerente = base[base['Gerente Vend'].notna() & (base['Gerente Vend'].astype(str).str.strip() != '')].copy()

        if base_com_gerente.empty:
            desenhar_linha_topo()
            print_centralizado("Nenhum gerente encontrado na base para analise.", Fore.RED, Style.BRIGHT)
            desenhar_linha_baixo()
            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao menu...")
            break

        ranking_gerentes = contar_clientes_por_coluna(base_com_gerente, 'Gerente Vend')

        desenhar_linha_topo()
        print_centralizado("ANALISE DE CARTEIRA POR GERENTE", Fore.MAGENTA, Style.BRIGHT)
        desenhar_linha_meio()
        print_linha_tabela_pendencias("GERENTE", "QTD CLIENTES")
        desenhar_linha_meio()

        for gerente_nome, qtd_clientes in ranking_gerentes.items():
            print_linha_tabela_pendencias(gerente_nome, qtd_clientes)

        desenhar_linha_meio()
        print_centralizado("Digite o nome ou codigo do gerente para aprofundar a analise.", Fore.GREEN)
        print_centralizado("Digite '0' ou 'voltar' para voltar ao menu.", Fore.GREEN)
        desenhar_linha_baixo()

        busca_gerente = input(Style.BRIGHT + "\n Buscar gerente: ").strip().lower()
        if busca_gerente in ['0', 'voltar', 'sair']:
            break
        if not busca_gerente:
            continue

        gerente_encontrado = None
        for gerente_nome in ranking_gerentes.index:
            if busca_gerente in gerente_nome.lower():
                gerente_encontrado = gerente_nome
                break

        if gerente_encontrado:
            dados_gerente = base_com_gerente[base_com_gerente['Gerente Vend'] == gerente_encontrado].copy()
            while True:
                # Resumos usados no cabecalho e no filtro do detalhamento final.
                ranking_vendedores = contar_clientes_por_coluna(dados_gerente, 'Vendedor')
                ranking_gestores = contar_clientes_por_coluna(dados_gerente, 'Vendedor Coo')

                limpar_tela()
                desenhar_linha_topo()
                print_centralizado(f"GERENTE SELECIONADO: {gerente_encontrado.upper()}", Fore.YELLOW, Style.BRIGHT)
                desenhar_linha_meio()
                print_esquerda(f"Total de clientes na carteira: {len(dados_gerente)}")
                desenhar_linha_baixo()

                print("\n")
                desenhar_linha_topo()
                print_centralizado("QUANTIDADE DE CLIENTES POR VENDEDOR", Fore.CYAN, Style.BRIGHT)
                desenhar_linha_meio()
                print_linha_tabela_pendencias("VENDEDOR", "QTD CLIENTES")
                desenhar_linha_meio()

                for vendedor_nome, qtd_clientes in ranking_vendedores.items():
                    print_linha_tabela_pendencias(vendedor_nome, qtd_clientes)

                desenhar_linha_baixo()

                print("\n")
                desenhar_linha_topo()
                print_centralizado("QUANTIDADE DE CLIENTES POR GESTOR", Fore.CYAN, Style.BRIGHT)
                desenhar_linha_meio()
                print_linha_tabela_pendencias("GESTOR", "QTD CLIENTES")
                desenhar_linha_meio()

                for gestor_nome, qtd_clientes in ranking_gestores.items():
                    print_linha_tabela_pendencias(gestor_nome, qtd_clientes)

                desenhar_linha_meio()
                print_centralizado("Pressione [ENTER] para abrir todos os clientes deste gerente.", Fore.GREEN)
                print_centralizado("Ou digite o nome/codigo do vendedor para filtrar a tabela final.", Fore.GREEN)
                print_centralizado("Digite '0' ou 'voltar' para escolher outro gerente.", Fore.GREEN)
                desenhar_linha_baixo()

                busca_vendedor = input(Style.BRIGHT + "\n Buscar vendedor ([ENTER] = todos): ").strip().lower()
                if busca_vendedor in ['0', 'voltar', 'sair']:
                    break

                dados_detalhados = dados_gerente.copy()
                vendedor_encontrado = None

                if busca_vendedor:
                    for vendedor_nome in ranking_vendedores.index:
                        if busca_vendedor in vendedor_nome.lower():
                            vendedor_encontrado = vendedor_nome
                            break

                    if not vendedor_encontrado:
                        print(Fore.RED + "\n Vendedor nao localizado dentro deste gerente.")
                        input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para tentar de novo...")
                        continue

                    dados_detalhados = dados_gerente[dados_gerente['Vendedor'].apply(valor_exibicao) == vendedor_encontrado].copy()

                # A tabela final exibe uma linha por cliente/filial dentro do recorte atual.
                dados_detalhados = dados_detalhados.sort_values(by=['Vendedor', 'Vendedor Coo', 'Repres. Ext.', 'Codigo', 'Loja'], na_position='last')
                tabela_final = montar_tabela_clientes(dados_detalhados)

                limpar_tela()
                desenhar_linha_topo()
                print_centralizado("TABELA FINAL DE CLIENTES", Fore.MAGENTA, Style.BRIGHT)
                desenhar_linha_meio()
                print_esquerda(f"Gerente: {gerente_encontrado}")
                if vendedor_encontrado:
                    print_esquerda(f"Vendedor filtrado: {vendedor_encontrado}")
                else:
                    print_esquerda("Vendedor filtrado: TODOS")
                print_esquerda(f"Total de clientes listados: {len(tabela_final)}")
                desenhar_linha_baixo()
                print(Fore.WHITE + tabela_final.to_string(index=False))
                input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao resumo do gerente...")
        else:
            print(Fore.RED + "\n Gerente nao localizado. Verifique o nome digitado.")
            input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para tentar de novo...")


# ---------------------------------------------------------------------
# OPÇÃO 3: EQUIPE DE VENDAS POR CLIENTE
# ---------------------------------------------------------------------
def menu_equipe_por_cliente(base):
    while True:
        limpar_tela()
        desenhar_linha_topo()
        print_centralizado("EQUIPE DE VENDAS POR CLIENTE", Fore.CYAN, Style.BRIGHT)
        desenhar_linha_meio()
        print_centralizado("Digite um ou varios CODLOJA separados por virgula.", Fore.GREEN)
        print_centralizado("Digite '0' ou 'voltar' para voltar ao menu.", Fore.GREEN)
        desenhar_linha_baixo()

        busca_cliente = input(Style.BRIGHT + "\n Buscar cliente(s): ").strip()
        if busca_cliente in ['0', 'voltar', 'sair']:
            break
        if not busca_cliente:
            continue

        # Pode receber um unico codigo parcial ou varios CodLoja completos.
        codlojas = normalizar_codlojas(busca_cliente)

        if len(codlojas) == 1 and len(codlojas[0]) <= 6:
            # Busca ampla quando o usuario informa so o codigo-base do cliente.
            linhas_cliente = base[base['Codigo'].astype(str).str.contains(codlojas[0], case=False, na=False)].copy()
            linhas_cliente = linhas_cliente.sort_values(by=['Codigo', 'Loja'])
        else:
            # Busca exata por cliente+loja quando ja veio CodLoja completo.
            linhas_cliente = base[base['CodLoja'].isin(codlojas)].copy()
            linhas_cliente['OrdemBusca'] = pd.Categorical(linhas_cliente['CodLoja'], categories=codlojas, ordered=True)
            linhas_cliente = linhas_cliente.sort_values(by=['OrdemBusca', 'Codigo', 'Loja']).drop(columns=['OrdemBusca'])

        if not linhas_cliente.empty:
            tabela_equipe = montar_tabela_equipe(linhas_cliente)

            print("\n")
            desenhar_linha_topo()
            print_centralizado("RESULTADO DA CONSULTA EM MASSA", Fore.MAGENTA, Style.BRIGHT)
            desenhar_linha_meio()
            print_esquerda(f"Total de registros localizados: {len(tabela_equipe)}")
            desenhar_linha_baixo()
            print(Fore.WHITE + tabela_equipe.to_string(index=False))

            if len(codlojas) > 1 or (len(codlojas) == 1 and len(codlojas[0]) > 6):
                encontrados = set(tabela_equipe['CodLoja'].astype(str).str.upper())
                nao_encontrados = [codigo for codigo in codlojas if codigo not in encontrados]

                # So faz sentido acusar ausencia quando a busca era por chaves completas.
                if nao_encontrados:
                    print(Fore.YELLOW + "\n CodLoja nao encontrados: " + ', '.join(nao_encontrados))
        else:
            print(Fore.RED + f"\n Cliente(s) '{busca_cliente}' nao localizado(s) na base.")

        input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para pesquisar de novo...")


# ---------------------------------------------------------------------
# OPÇÃO 4: PAINEL DE GESTOR SEM VENDEDOR INTERNO
# ---------------------------------------------------------------------
def menu_gestor_sem_vendedor(base):
    while True:
        limpar_tela()

        # Localiza clientes com gestor preenchido, mas sem vendedor interno vinculado.
        condicao = (base['Vendedor_Original'].isna() | (base['Vendedor_Original'].astype(str).str.strip() == '')) & base['Vendedor Coo'].notna()
        dados_filtrados = base[condicao].copy()
        dados_filtrados = dados_filtrados[dados_filtrados['Gerente Vend'].notna() & (dados_filtrados['Gerente Vend'].astype(str).str.strip() != '')]

        if dados_filtrados.empty:
            desenhar_linha_topo()
            print_centralizado("🎉 EXCELENTE! Nenhum Gestor órfão de Vendedor Interno na base.", Fore.GREEN, Style.BRIGHT)
            desenhar_linha_baixo()
            input("\nPressione [ENTER] para voltar ao menu...")
            break

        total_geral_erros = len(dados_filtrados)

        desenhar_linha_topo()
        print_centralizado(f"📊 TOTAL GERAL DE PENDÊNCIAS NA BASE: {total_geral_erros} CLIENTE(S) 📊", Fore.RED, Style.BRIGHT)
        desenhar_linha_meio()
        print_centralizado("PAINEL MACRO: RANKING DE GERENTES COM PENDÊNCIAS", Fore.YELLOW, Style.BRIGHT)
        desenhar_linha_meio()

        hc1 = "👔 GERENTE VENDAS (GERVEN)".ljust(76)
        hc2 = "QTD OCORRÊNCIAS".center(18)
        print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + hc1 + Fore.BLUE + Style.BRIGHT + "│" + Fore.WHITE + hc2 + Fore.BLUE + Style.BRIGHT + " │")
        desenhar_linha_meio()

        ranking_gervens = dados_filtrados['Gerente Vend'].value_counts()

        for gerven_nome, total_gerven in ranking_gervens.items():
            print_linha_gerven_macro(f"👔 {gerven_nome.upper()}", total_gerven)

        desenhar_linha_baixo()

        busca_gerven = input(Style.BRIGHT + "\n 🔍 Digite o nome ou código do Gerente (ou '0' para voltar): ").strip().lower()
        if busca_gerven in ['0', 'voltar', 'sair', '']:
            break

        gerven_encontrado = None
        for gerven_nome in ranking_gervens.index:
            if busca_gerven in gerven_nome.lower():
                gerven_encontrado = gerven_nome
                break

        if gerven_encontrado:
            # --- ETAPA 2: SUBMENU DO GERENTE SELECIONADO ---
            while True:
                limpar_tela()
                desenhar_linha_topo()
                print_centralizado(f"GERENTE SELECIONADO: {gerven_encontrado.upper()}", Fore.MAGENTA, Style.BRIGHT)
                desenhar_linha_meio()
                print_esquerda("[1] Ver a quantidade detalhada por GESTOR", Fore.CYAN)
                print_esquerda("[2] Ver TODOS os clientes deste Gerente (Tela de Auditoria)", Fore.CYAN)
                print_esquerda("", Fore.WHITE)
                print_esquerda("[0] Voltar para o Ranking de Gerentes", Fore.RED)
                desenhar_linha_baixo()

                sub_opcao = input(Style.BRIGHT + "\n 👉 Escolha uma opção: ").strip()

                if sub_opcao == '0' or sub_opcao.lower() == 'voltar':
                    break

                elif sub_opcao == '1':
                    while True:
                        limpar_tela()
                        desenhar_linha_topo()
                        print_centralizado(f"QUANTIDADE POR GESTOR - {gerven_encontrado.upper()}", Fore.YELLOW, Style.BRIGHT)
                        desenhar_linha_meio()

                        # Dentro do gerente, o primeiro detalhamento quebra por gestor/coordenador.
                        dados_gerven = dados_filtrados[dados_filtrados['Gerente Vend'] == gerven_encontrado]
                        ranking_gestores = dados_gerven['Vendedor Coo'].value_counts()

                        for gestor_nome, qtd_gestor in ranking_gestores.items():
                            print_linha_gestor_macro(gestor_nome, qtd_gestor)

                        desenhar_linha_baixo()

                        busca_gestor = input(Style.BRIGHT + "\n 🔍 Digite o nome do Gestor para ver seus clientes (ou [ENTER] para voltar): ").strip().lower()
                        if not busca_gestor or busca_gestor in ['0', 'voltar']:
                            break

                        gestor_encontrado = None
                        for g_nome in ranking_gestores.index:
                            if busca_gestor in g_nome.lower():
                                gestor_encontrado = g_nome
                                break

                        if gestor_encontrado:
                            limpar_tela()
                            clientes_do_gestor = dados_gerven[dados_gerven['Vendedor Coo'] == gestor_encontrado]
                            clientes_do_gestor = clientes_do_gestor.sort_values(by='Codigo')
                            total_oc_gestor = len(clientes_do_gestor)

                            desenhar_linha_topo()
                            print_centralizado(f"LISTA DE CLIENTES DO GESTOR: {gestor_encontrado.upper()}", Fore.MAGENTA, Style.BRIGHT)
                            print_centralizado(f"Total de pendências: {total_oc_gestor} cliente(s)", Fore.YELLOW)
                            desenhar_linha_meio()

                            th1 = "CLIENTE-LOJA".ljust(12)
                            th2 = "GESTOR VINCULADO".ljust(28)
                            th3 = "NOME DO CLIENTE".ljust(38)
                            th4 = "VEND INTERNO".center(14)
                            print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th1 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th2 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th3 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th4 + " │")
                            desenhar_linha_meio()

                            for idx, row in clientes_do_gestor.iterrows():
                                cod_completo = f"{row['Codigo']}{row['Loja']}"
                                nome_do_cliente = str(row['Nome']) if 'Nome' in base.columns else "NOME NÃO ENCONTRADO"
                                print_linha_tabela_limpeza(cod_completo, row['Vendedor Coo'], nome_do_cliente, row['Vendedor_Original'])

                            desenhar_linha_baixo()
                            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao ranking de Gestores...")
                        else:
                            print(Fore.RED + "\n ❌ Gestor não localizado. Verifique o nome digitado.")
                            input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para tentar de novo...")

                elif sub_opcao == '2':
                    limpar_tela()
                    # Visao direta de todos os clientes pendentes daquele gerente.
                    clientes_do_gerven = dados_filtrados[dados_filtrados['Gerente Vend'] == gerven_encontrado]
                    clientes_do_gerven = clientes_do_gerven.sort_values(by=['Vendedor Coo', 'Codigo'])
                    total_ocorrencias = len(clientes_do_gerven)

                    desenhar_linha_topo()
                    print_centralizado(f"LISTA DE CLIENTES: {gerven_encontrado.upper()}", Fore.MAGENTA, Style.BRIGHT)
                    print_centralizado(f"Total de pendências: {total_ocorrencias} cliente(s)", Fore.YELLOW)
                    desenhar_linha_meio()

                    th1 = "CLIENTE-LOJA".ljust(12)
                    th2 = "GESTOR VINCULADO".ljust(28)
                    th3 = "NOME DO CLIENTE".ljust(38)
                    th4 = "VEND INTERNO".center(14)
                    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th1 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th2 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th3 + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + th4 + " │")
                    desenhar_linha_meio()

                    for idx, row in clientes_do_gerven.iterrows():
                        cod_completo = f"{row['Codigo']}{row['Loja']}"
                        nome_do_cliente = str(row['Nome']) if 'Nome' in base.columns else "NOME NÃO ENCONTRADO"
                        print_linha_tabela_limpeza(cod_completo, row['Vendedor Coo'], nome_do_cliente, row['Vendedor_Original'])

                    desenhar_linha_baixo()
                    input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao menu do Gerente...")
        else:
            print(Fore.RED + "\n ❌ Gerente não localizado. Verifique o nome digitado.")
            input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para continuar...")


# ---------------------------------------------------------------------
# OPÇÃO 5: ANALISE DE CARTEIRAS VENDEDORES
# ---------------------------------------------------------------------
def menu_analise_vendedores(base):
    import os
    while True:
        limpar_tela()
        # Essa analise destaca vendedores que aparecem amarrados a mais de um gerente.
        base_com_vendedor = base[base['Vendedor'].notna() & (base['Vendedor'].astype(str).str.strip() != '')].copy()

        if base_com_vendedor.empty:
            desenhar_linha_topo()
            print_centralizado("Nenhum vendedor encontrado na base para analise.", Fore.RED, Style.BRIGHT)
            desenhar_linha_baixo()
            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao menu...")
            break

        # Resumo principal: um vendedor entra no painel apenas se tiver mais de um gerente.
        resumo_vendedores = base_com_vendedor.groupby('Vendedor').agg(
            Qtd_Clientes=('Codigo', 'count'),
            Qtd_Gerentes=('Gerente Vend', lambda s: s.apply(valor_exibicao).nunique())
        ).reset_index()
        resumo_vendedores = resumo_vendedores.sort_values(by=['Qtd_Gerentes', 'Qtd_Clientes', 'Vendedor'], ascending=[False, False, True])
        resumo_vendedores = resumo_vendedores[resumo_vendedores['Qtd_Gerentes'] > 1].copy()

        if resumo_vendedores.empty:
            desenhar_linha_topo()
            print_centralizado("Nenhum vendedor com mais de 1 gerente foi encontrado na base.", Fore.GREEN, Style.BRIGHT)
            desenhar_linha_baixo()
            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao menu...")
            break

        # Mapa auxiliar usado para exibir, logo abaixo do vendedor, o desdobramento por gerente.
        detalhe_gerentes_vendedor = base_com_vendedor[base_com_vendedor['Vendedor'].isin(resumo_vendedores['Vendedor'])].copy()
        detalhe_gerentes_vendedor['Gerente_Exibicao'] = detalhe_gerentes_vendedor['Gerente Vend'].apply(valor_exibicao)
        detalhe_gerentes_vendedor = detalhe_gerentes_vendedor.groupby(['Vendedor', 'Gerente_Exibicao']).size().reset_index(name='Qtd_Clientes')
        detalhe_gerentes_vendedor = detalhe_gerentes_vendedor.sort_values(by=['Vendedor', 'Qtd_Clientes', 'Gerente_Exibicao'], ascending=[True, True, True])
        mapa_gerentes_vendedor = {
            vendedor: list(grupo[['Gerente_Exibicao', 'Qtd_Clientes']].itertuples(index=False, name=None))
            for vendedor, grupo in detalhe_gerentes_vendedor.groupby('Vendedor')
        }

        desenhar_linha_topo()
        print_centralizado("ANALISE DE CARTEIRAS VENDEDORES", Fore.MAGENTA, Style.BRIGHT)
        desenhar_linha_meio()
        print_linha_tabela_pendencias("VENDEDOR [QTD GERENTES]", "QTD CLIENTES")
        desenhar_linha_meio()

        for _, row in resumo_vendedores.iterrows():
            descricao_vendedor = f"{row['Vendedor']} [{row['Qtd_Gerentes']} gerente(s)]"
            print_linha_tabela_pendencias(descricao_vendedor, row['Qtd_Clientes'])
            for gerente_nome, qtd_clientes in mapa_gerentes_vendedor.get(row['Vendedor'], []):
                print_linha_gestor_macro(gerente_nome, qtd_clientes)

        desenhar_linha_meio()
        print_centralizado("Digite o nome ou codigo do vendedor para aprofundar a analise.", Fore.GREEN)
        print_centralizado("Digite 'todos' para visualizar todos os clientes de todos os vendedores listados.", Fore.GREEN)
        print_centralizado("Digite '0' ou 'voltar' para voltar ao menu.", Fore.GREEN)
        desenhar_linha_baixo()

        busca_vendedor = input(Style.BRIGHT + "\n Buscar vendedor: ").strip().lower()
        if busca_vendedor in ['0', 'voltar', 'sair']:
            break
        if not busca_vendedor:
            continue

        if busca_vendedor in ['todos', 'tudo']:
            # Exporta tudo para Excel quando o usuario quer a visao completa de todos os casos.
            dados_todos = base_com_vendedor[base_com_vendedor['Vendedor'].isin(resumo_vendedores['Vendedor'])].copy()
            dados_todos = dados_todos.sort_values(by=['Vendedor', 'Gerente Vend', 'Vendedor Coo', 'Repres. Ext.', 'Codigo', 'Loja'], na_position='last')
            tabela_todos = montar_tabela_equipe(dados_todos, limitar_texto=False)
            caminho_excel = exportar_analise_vendedores_excel(resumo_vendedores, detalhe_gerentes_vendedor, tabela_todos)

            limpar_tela()
            desenhar_linha_topo()
            print_centralizado("ARQUIVO EXCEL GERADO COM SUCESSO", Fore.MAGENTA, Style.BRIGHT)
            desenhar_linha_meio()
            print_esquerda(f"Total de vendedores listados: {len(resumo_vendedores)}")
            print_esquerda(f"Total de clientes listados: {len(tabela_todos)}")
            print_esquerda(f"Arquivo: {os.path.basename(caminho_excel)}")
            print_esquerda(f"Pasta: {os.path.dirname(caminho_excel)}")
            desenhar_linha_baixo()
            input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar...")
            continue

        vendedor_encontrado = None
        for vendedor_nome in resumo_vendedores['Vendedor']:
            if busca_vendedor in vendedor_nome.lower():
                vendedor_encontrado = vendedor_nome
                break

        if vendedor_encontrado:
            dados_vendedor = base_com_vendedor[base_com_vendedor['Vendedor'] == vendedor_encontrado].copy()

            while True:
                # Reconta os gerentes do vendedor selecionado para montar o submenu.
                ranking_gerentes_vendedor = contar_clientes_por_coluna(dados_vendedor, 'Gerente Vend').sort_values(ascending=True)

                limpar_tela()
                desenhar_linha_topo()
                print_centralizado(f"VENDEDOR SELECIONADO: {vendedor_encontrado.upper()}", Fore.YELLOW, Style.BRIGHT)
                desenhar_linha_meio()
                print_esquerda(f"Total de clientes na carteira: {len(dados_vendedor)}")
                print_esquerda(f"Total de gerentes vinculados: {len(ranking_gerentes_vendedor)}")
                desenhar_linha_baixo()

                print("\n")
                desenhar_linha_topo()
                print_centralizado("CONTAGEM DE CLIENTES POR GERENTE", Fore.CYAN, Style.BRIGHT)
                desenhar_linha_meio()
                print_linha_tabela_pendencias("GERENTE", "QTD CLIENTES")
                desenhar_linha_meio()

                for gerente_nome, qtd_clientes in ranking_gerentes_vendedor.items():
                    print_linha_tabela_pendencias(gerente_nome, qtd_clientes)

                desenhar_linha_meio()
                print_centralizado("Pressione [ENTER] para abrir todos os clientes deste vendedor.", Fore.GREEN)
                print_centralizado("Ou digite o nome/codigo do gerente para filtrar a tabela final.", Fore.GREEN)
                print_centralizado("Digite '0' ou 'voltar' para escolher outro vendedor.", Fore.GREEN)
                desenhar_linha_baixo()

                busca_gerente = input(Style.BRIGHT + "\n Buscar gerente ([ENTER] = todos): ").strip().lower()
                if busca_gerente in ['0', 'voltar', 'sair']:
                    break

                dados_detalhados = dados_vendedor.copy()
                gerente_encontrado = None

                if busca_gerente:
                    for gerente_nome in ranking_gerentes_vendedor.index:
                        if busca_gerente in gerente_nome.lower():
                            gerente_encontrado = gerente_nome
                            break

                    if not gerente_encontrado:
                        print(Fore.RED + "\n Gerente nao localizado dentro deste vendedor.")
                        input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para tentar de novo...")
                        continue

                    dados_detalhados = dados_vendedor[dados_vendedor['Gerente Vend'].apply(valor_exibicao) == gerente_encontrado].copy()

                # Ordena para a tabela final sair agrupada naturalmente por hierarquia comercial.
                dados_detalhados = dados_detalhados.sort_values(by=['Gerente Vend', 'Vendedor Coo', 'Repres. Ext.', 'Codigo', 'Loja'], na_position='last')
                tabela_final = montar_tabela_equipe(dados_detalhados)

                limpar_tela()
                desenhar_linha_topo()
                print_centralizado("TABELA FINAL DE CLIENTES", Fore.MAGENTA, Style.BRIGHT)
                desenhar_linha_meio()
                print_esquerda(f"Vendedor: {vendedor_encontrado}")
                if gerente_encontrado:
                    print_esquerda(f"Gerente filtrado: {gerente_encontrado}")
                else:
                    print_esquerda("Gerente filtrado: TODOS")
                print_esquerda(f"Total de clientes listados: {len(tabela_final)}")
                desenhar_linha_baixo()
                print(Fore.WHITE + tabela_final.to_string(index=False))
                input(Fore.LIGHTBLACK_EX + "\nPressione [ENTER] para voltar ao resumo do vendedor...")
        else:
            print(Fore.RED + "\n Vendedor nao localizado. Verifique o nome digitado.")
            input(Fore.LIGHTBLACK_EX + "Pressione [ENTER] para tentar de novo...")
