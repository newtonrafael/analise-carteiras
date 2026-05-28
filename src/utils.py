import os
import pandas as pd
from colorama import Fore, Back, Style, init

# Inicializa o colorama
init(autoreset=True)

# --- CONFIGURAÇÃO VISUAL DA TABELA ---
LARGURA_TABELA = 100
TEXTO_SEM_VINCULO = ''

# --- FUNÇÃO PARA LIMPAR A TELA ---
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- FUNÇÕES DE BORDA DA TABELA ---
def desenhar_linha_topo():
    print(Fore.BLUE + Style.BRIGHT + "┌" + "─" * (LARGURA_TABELA - 2) + "┐")

def desenhar_linha_meio():
    print(Fore.BLUE + Style.BRIGHT + "├" + "─" * (LARGURA_TABELA - 2) + "┤")

def desenhar_linha_baixo():
    print(Fore.BLUE + Style.BRIGHT + "└" + "─" * (LARGURA_TABELA - 2) + "┘")

def print_centralizado(texto, cor=Fore.WHITE, estilo=Style.NORMAL):
    # Remove os codigos de cor do calculo para manter o alinhamento visual.
    texto_puro = texto.replace(Fore.CYAN, "").replace(Fore.WHITE, "").replace(Fore.RED, "").replace(Fore.YELLOW, "").replace(Fore.GREEN, "").replace(Fore.MAGENTA, "")
    espacos_totais = (LARGURA_TABELA - 2) - len(texto_puro)
    espaco_esquerda = espacos_totais // 2
    espaco_direita = espacos_totais - espaco_esquerda
    print(Fore.BLUE + Style.BRIGHT + "│" + " " * espaco_esquerda + estilo + cor + texto + Fore.BLUE + Style.BRIGHT + " " * espaco_direita + "│")

def print_esquerda(texto, cor=Fore.WHITE, estilo=Style.NORMAL):
    # Mesmo cuidado do centralizado, mas com texto ancorado a esquerda.
    texto_puro = texto.replace(Fore.CYAN, "").replace(Fore.WHITE, "").replace(Fore.RED, "").replace(Fore.YELLOW, "").replace(Fore.GREEN, "").replace(Fore.MAGENTA, "")
    espaco_direita = (LARGURA_TABELA - 4) - len(texto_puro)
    print(Fore.BLUE + Style.BRIGHT + "│ " + estilo + cor + texto + " " * espaco_direita + Fore.BLUE + Style.BRIGHT + " │")

# --- FUNÇÕES DE LINHAS DE TABELA ---
def print_linha_tabela_pendencias(colaborador, qtd):
    col_colab = str(colaborador)[:76].ljust(76)
    col_qtd = str(qtd).center(18)
    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + col_colab + Fore.BLUE + Style.BRIGHT + "│" + Fore.CYAN + col_qtd + Fore.BLUE + Style.BRIGHT + " │")

def print_linha_gerven_macro(gerven, qtd):
    col_gerven = str(gerven)[:76].ljust(76)
    col_qtd = f"{qtd} cliente(s)".center(18)
    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + Style.BRIGHT + col_gerven + Fore.BLUE + Style.BRIGHT + "│" + Fore.GREEN + Style.BRIGHT + col_qtd + Fore.BLUE + Style.BRIGHT + " │")

def print_linha_gestor_macro(gestor, qtd):
    col_gestor = f"   └─ 👤 {gestor}"[:76].ljust(76)
    col_qtd = f"{qtd} cliente(s)".center(18)
    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.CYAN + col_gestor + Fore.BLUE + Style.BRIGHT + "│" + Fore.YELLOW + col_qtd + Fore.BLUE + Style.BRIGHT + " │")

def print_linha_tabela_limpeza(cliente_loja, gestor, nome_cliente, vend_original):
    col_cli = str(cliente_loja)[:12].ljust(12)
    col_coo = str(gestor)[:28].ljust(28)
    col_nom = str(nome_cliente)[:38].ljust(38)
    col_ven = f"[{str(vend_original).strip()}]"[:14].center(14)
    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + col_cli + Fore.BLUE + Style.BRIGHT + "│ " + Fore.CYAN + col_coo + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + col_nom + Fore.BLUE + Style.BRIGHT + "│" + Fore.RED + col_ven + Fore.BLUE + Style.BRIGHT + " │")

def print_linha_raio_x(papel, colaborador):
    col_papel = str(papel)[:20].ljust(20)
    col_colab = str(colaborador)[:74].ljust(74)
    print(Fore.BLUE + Style.BRIGHT + "│ " + Fore.YELLOW + col_papel + Fore.BLUE + Style.BRIGHT + "│ " + Fore.WHITE + col_colab + Fore.BLUE + Style.BRIGHT + " │")

# --- HELPERS DE DADOS ---
def contar_clientes_por_coluna(df, coluna):
    valores = df[coluna].fillna(TEXTO_SEM_VINCULO).astype(str).str.strip()
    valores = valores.replace({'': TEXTO_SEM_VINCULO, 'nan': TEXTO_SEM_VINCULO, '<NA>': TEXTO_SEM_VINCULO})
    return valores.value_counts()

def valor_exibicao(valor, vazio=TEXTO_SEM_VINCULO):
    if pd.isna(valor):
        return vazio
    texto = str(valor).strip()
    if texto in ['', 'nan', '<NA>']:
        return vazio
    return texto

def normalizar_codlojas(texto):
    # Aceita entrada com virgula, ponto e virgula ou quebra de linha e remove repetidos.
    codigos = []
    vistos = set()

    for item in texto.replace('\n', ',').replace(';', ',').split(','):
        codigo = item.strip().upper()
        if codigo and codigo not in vistos:
            vistos.add(codigo)
            codigos.append(codigo)

    return codigos
