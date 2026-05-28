# Sistema de Auditoria e Consulta de Carteiras

Sistema de terminal para auditoria e consulta de carteiras comerciais com base em dados exportados do ERP Protheus.

Permite identificar inconsistências nos vínculos comerciais, consultar a equipe de vendas por cliente e exportar análises para Excel.

---

## Funcionalidades

- Painel de carteiras com menos de 30 clientes (possíveis inconsistências)
- Análise de carteira por gerente, com detalhamento por vendedor e gestor
- Consulta da equipe comercial por cliente (CodLoja)
- Painel de gestores sem vendedor interno vinculado
- Análise de vendedores com múltiplos gerentes
- Exportação para Excel com abas de resumo e detalhamento

---

## Tecnologias

- Python
- Pandas
- OpenPyXL
- Colorama

---

## Estrutura

```
projeto_analise_carteiras/
│
├── data/
│   ├── base.csv
│   └── mata030.csv
│
├── output/
│
├── src/
│   ├── __init__.py
│   ├── exportacao.py
│   ├── tratamento.py
│   ├── utils.py
│   └── visual.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Como executar

```bash
git clone URL_DO_REPOSITORIO
pip install -r requirements.txt
python main.py
```

Coloque os arquivos `base.csv` e `mata030.csv` na pasta `data/` antes de executar.

---

## Observações

Os dados deste repositório são fictícios. Nomes, códigos e informações foram substituídos para preservar a confidencialidade dos dados reais utilizados internamente.
