from colorama import Fore, Style

from src.utils import limpar_tela, desenhar_linha_topo, desenhar_linha_meio, desenhar_linha_baixo, print_esquerda
from src.tratamento import carregar_dados
from src.visual import (
    menu_pendencias,
    menu_carteira_gerente,
    menu_equipe_por_cliente,
    menu_gestor_sem_vendedor,
    menu_analise_vendedores,
)

# --- CARGA E TRATAMENTO DOS DADOS ---
base = carregar_dados(
    caminho_base='data/base.csv',
    caminho_nomes='data/mata030.csv'
)

# Lista em memoria para esconder pendencias ja tratadas durante a sessao atual.
colaboradores_ajustados = []

# ==========================================
# MENU PRINCIPAL INTERATIVO
# ==========================================
while True:
    limpar_tela()
    desenhar_linha_topo()
    print_esquerda("SISTEMA DE AUDITORIA E CONSULTA", Fore.WHITE, Style.BRIGHT)
    desenhar_linha_meio()
    print_esquerda("[1] Carteiras Possivelmente Incorretas (< 30 clientes)", Fore.CYAN)
    print_esquerda("[2] Analise de Carteira por Gerente", Fore.CYAN)
    print_esquerda("[3] Equipe de Vendas por Cliente", Fore.CYAN)
    print_esquerda("[4] Painel de Gestor sem Vendedor Interno (por Gerven)", Fore.YELLOW)
    print_esquerda("[5] Analise de Carteiras Vendedores", Fore.CYAN)
    print_esquerda("", Fore.WHITE)
    print_esquerda("[0] Sair do Programa", Fore.RED)
    desenhar_linha_baixo()

    opcao = input(Style.BRIGHT + "\n 👉 Escolha uma opção: ").strip()

    if opcao == '1':
        menu_pendencias(base, colaboradores_ajustados)

    elif opcao == '2':
        menu_carteira_gerente(base)

    elif opcao == '3':
        menu_equipe_por_cliente(base)

    elif opcao == '4':
        menu_gestor_sem_vendedor(base)

    elif opcao == '5':
        menu_analise_vendedores(base)

    elif opcao == '0':
        limpar_tela()
        print("\n" + Fore.GREEN + Style.BRIGHT + " 🎉 Encerrando o sistema. Bom trabalho!")
        break
