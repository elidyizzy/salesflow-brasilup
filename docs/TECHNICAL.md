# Documentação Técnica - SalesFlow

## Índice

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Estrutura de Arquivos](#estrutura-de-arquivos)
3. [Módulos do Sistema](#módulos-do-sistema)
4. [Modelos de Dados](#modelos-de-dados)
5. [APIs Externas](#apis-externas)
6. [Fluxos de Dados](#fluxos-de-dados)
7. [Geração de PDF](#geração-de-pdf)
8. [Configurações](#configurações)
9. [Deploy e Infraestrutura](#deploy-e-infraestrutura)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral da Arquitetura

### Stack Tecnológico

| Camada | Tecnologia | Versão | Função |
|--------|------------|--------|--------|
| Frontend | Streamlit | 1.31.0 | Interface web reativa |
| Backend | Python | 3.10+ | Lógica de negócio |
| PDF Engine | FPDF2 | 2.7.8 | Geração de documentos |
| HTTP Client | Requests | 2.31.0 | Consumo de APIs |
| Persistência | JSON | - | Armazenamento local |

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                               │
│                    (Browser/Mobile)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLOUDFLARE                              │
│                   (DNS + SSL + Proxy)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       RAILWAY                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    STREAMLIT APP                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │   app.py    │  │ gerar_pdf.py│  │   *.json    │   │  │
│  │  │  (Routes)   │  │  (PDF Gen)  │  │   (Data)    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │BrasilAPI │   │  ViaCEP  │   │  Local   │
    │  (CNPJ)  │   │  (CEP)   │   │  Files   │
    └──────────┘   └──────────┘   └──────────┘
```

---

## Estrutura de Arquivos

```
salesflow-brasilup/
│
├── app.py                      # Aplicação principal (900+ linhas)
│   ├── Configuração Streamlit
│   ├── Funções de dados (CRUD)
│   ├── Funções de API (CNPJ/CEP)
│   ├── Lógica de numeração ORS
│   ├── Interface (Tabs)
│   └── Session State Management
│
├── gerar_pdf.py                # Motor de geração de PDF
│   ├── Classe PDFOrcamento
│   ├── Header/Footer customizados
│   └── Função gerar_pdf_orcamento()
│
├── catalogo.json               # Configurações e produtos
├── clientes.json               # Base de clientes (runtime)
├── orcamentos.json             # Base de orçamentos (runtime)
│
├── .streamlit/
│   └── config.toml             # Tema visual
│
├── logo.png                    # Logo Brasil UP (PDF)
├── logo_bedata.png             # Logo Be Data (App)
│
├── Procfile                    # Configuração Railway
├── requirements.txt            # Dependências Python
└── README.md                   # Documentação usuário
```

---

## Módulos do Sistema

### 1. app.py - Aplicação Principal

#### 1.1 Imports e Configuração

```python
import streamlit as st
import json
from datetime import datetime, timedelta
import requests

st.set_page_config(
    page_title="SalesFlow by GEN.IA",
    page_icon="🧠",
    layout="wide"
)
```

#### 1.2 Funções de Persistência

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `carregar_catalogo()` | Carrega produtos e config | `dict` |
| `salvar_catalogo(data)` | Salva catálogo | `None` |
| `carregar_clientes()` | Carrega base de clientes | `dict` |
| `salvar_clientes(data)` | Salva clientes | `None` |
| `carregar_orcamentos()` | Carrega orçamentos | `dict` |
| `salvar_orcamentos(data)` | Salva orçamentos | `None` |

#### 1.3 Funções de API

```python
def consultar_cnpj(cnpj: str) -> dict | None:
    """
    Consulta dados de empresa via BrasilAPI.

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        dict com dados da empresa ou None se não encontrado

    Exemplo de retorno:
    {
        "razao_social": "EMPRESA LTDA",
        "nome_fantasia": "EMPRESA",
        "cnpj": "12345678000190",
        "email": "contato@empresa.com",
        "ddd_telefone_1": "31999999999",
        "logradouro": "Rua Example",
        "numero": "123",
        "bairro": "Centro",
        "municipio": "Belo Horizonte",
        "uf": "MG",
        "cep": "30000000"
    }
    """
```

```python
def consultar_cep(cep: str) -> dict | None:
    """
    Consulta endereço via ViaCEP.

    Args:
        cep: CEP com ou sem formatação

    Returns:
        dict com dados do endereço ou None

    Exemplo de retorno:
    {
        "logradouro": "Rua Example",
        "bairro": "Centro",
        "localidade": "Belo Horizonte",
        "uf": "MG"
    }
    """
```

#### 1.4 Sistema de Numeração ORS

```python
def gerar_numero_orcamento() -> str:
    """
    Gera número único de orçamento.

    Formato: ORS + MM + SEQ (3 dígitos)
    - MM: Mês atual (01-12)
    - SEQ: Sequência iniciando em 100

    Exemplos:
    - Janeiro, 1º orçamento: ORS01100
    - Janeiro, 2º orçamento: ORS01101
    - Fevereiro, 1º orçamento: ORS02100

    A sequência é persistida em orcamentos.json
    """
    data = carregar_orcamentos()
    mes_atual = datetime.now().strftime("%m")

    seq = data["sequencia"].get(mes_atual, 99) + 1
    data["sequencia"][mes_atual] = seq
    salvar_orcamentos(data)

    return f"ORS{mes_atual}{seq:03d}"
```

#### 1.5 Session State

| Chave | Tipo | Descrição |
|-------|------|-----------|
| `itens` | `list[dict]` | Itens do orçamento atual |
| `dados_cnpj` | `dict\|None` | Cache da consulta CNPJ |
| `numero_orcamento` | `str\|None` | Número do orçamento em edição |
| `editando` | `bool` | Flag de modo edição |
| `cli_*` | `str` | Campos do cliente |

---

### 2. gerar_pdf.py - Motor de PDF

#### 2.1 Classe PDFOrcamento

```python
class PDFOrcamento(FPDF):
    """
    Classe customizada para geração de orçamentos em PDF.
    Herda de FPDF e implementa header/footer personalizados.

    Attributes:
        dados (dict): Dados do orçamento para renderização
    """

    def __init__(self, dados: dict):
        super().__init__()
        self.dados = dados
        self.set_auto_page_break(auto=True, margin=30)

    def header(self):
        """Renderiza cabeçalho com logo e slogan."""
        # Fundo azul claro
        self.set_fill_color(232, 244, 252)
        self.rect(0, 0, 210, 42, 'F')

        # Logo da empresa
        self.image("logo.png", x=145, y=8, w=50)

        # Slogan
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 90, 138)
        self.cell(100, 6, self.dados['empresa']['slogan'])

    def footer(self):
        """Renderiza rodapé com informações de contato."""
        self.set_y(-25)
        # Site, email, endereço, página
```

#### 2.2 Função Principal

```python
def gerar_pdf_orcamento(dados: dict) -> bytes:
    """
    Gera PDF do orçamento completo.

    Args:
        dados: Dicionário com todos os dados do orçamento

    Returns:
        bytes do PDF gerado

    Estrutura esperada de 'dados':
    {
        "numero": "ORS01100",
        "data": "29/01/2026",
        "expiracao": "28/02/2026",
        "vendedor": "Nome do Vendedor",
        "cliente": {
            "nome": "EMPRESA LTDA",
            "endereco": "Rua X, 123",
            "cidade": "Cidade",
            "estado": "UF",
            "cep": "00000-000",
            "cnpj": "00.000.000/0000-00"
        },
        "itens": [
            {
                "descricao": "PRODUTO X",
                "quantidade": 10,
                "preco_unitario": 49.90,
                "valor_total": 499.00
            }
        ],
        "total": 499.00,
        "empresa": {...},
        "observacoes": "Texto livre"
    }
    """
```

#### 2.3 Layout do PDF

```
┌────────────────────────────────────────────────┐
│  SLOGAN                              [LOGO]    │  <- Header (42mm)
├────────────────────────────────────────────────┤
│  CLIENTE                    Cotação n. ORSXXXX │
│  Endereço                                      │
│  Cidade/UF/CEP                                 │
│  CPF/CNPJ: XX.XXX.XXX/XXXX-XX                 │
├────────────────────────────────────────────────┤
│  DATA        │  EXPIRAÇÃO   │  VENDEDOR       │  <- Info Box
│  DD/MM/YYYY  │  DD/MM/YYYY  │  Nome           │
├────────────────────────────────────────────────┤
│  DESCRIÇÃO   │  QTD  │  PREÇO UN. │  VALOR    │  <- Tabela
│  Produto 1   │  10   │  R$ 49,90  │  R$ 499   │
│  Produto 2   │  20   │  R$ 29,90  │  R$ 598   │
├────────────────────────────────────────────────┤
│                        TOTAL │  R$ 1.097,00   │
├────────────────────────────────────────────────┤
│  INFORMAÇÕES IMPORTANTES                       │
│  Observações do orçamento...                   │
├────────────────────────────────────────────────┤
│  www.site.com.br                               │  <- Footer
│  email@empresa.com                             │
│  Endereço completo                             │
│  Página X                                      │
└────────────────────────────────────────────────┘
```

---

## Modelos de Dados

### catalogo.json

```json
{
  "empresa": {
    "nome": "string",
    "endereco": "string",
    "slogan": "string",
    "site": "string",
    "logo_url": "string"
  },
  "vendedores": ["string"],
  "validade_dias": "number",
  "tamanhos_padrao": {
    "camisas": ["string"],
    "calcas": ["string"]
  },
  "produtos": [
    {
      "categoria": "string",
      "nome": "string",
      "preco": "number"
    }
  ]
}
```

### clientes.json

```json
{
  "empresas": [
    {
      "id": "number",
      "tipo": "PJ",
      "razao_social": "string",
      "nome_fantasia": "string",
      "cnpj": "string",
      "ie": "string",
      "email": "string",
      "telefone": "string",
      "endereco": {
        "logradouro": "string",
        "numero": "string",
        "complemento": "string",
        "bairro": "string",
        "cidade": "string",
        "uf": "string",
        "cep": "string"
      },
      "contatos": [
        {
          "nome": "string",
          "cargo": "string",
          "email": "string",
          "telefone": "string"
        }
      ],
      "data_cadastro": "YYYY-MM-DD HH:MM"
    }
  ],
  "pessoas": [
    {
      "id": "number",
      "tipo": "PF",
      "nome": "string",
      "cpf": "string",
      "rg": "string",
      "email": "string",
      "telefone": "string",
      "whatsapp": "string",
      "endereco": {...},
      "data_cadastro": "YYYY-MM-DD HH:MM"
    }
  ]
}
```

### orcamentos.json

```json
{
  "orcamentos": [
    {
      "numero": "ORS01100",
      "data": "DD/MM/YYYY",
      "data_iso": "YYYY-MM-DD",
      "expiracao": "DD/MM/YYYY",
      "vendedor": "string",
      "cliente": {
        "nome": "string",
        "contato": "string",
        "endereco": "string",
        "cidade": "string",
        "estado": "string",
        "cep": "string",
        "cnpj": "string"
      },
      "itens": [
        {
          "descricao": "string",
          "quantidade": "number",
          "preco_unitario": "number",
          "valor_total": "number"
        }
      ],
      "total": "number",
      "empresa": {...},
      "observacoes": "string"
    }
  ],
  "sequencia": {
    "01": 100,
    "02": 100
  }
}
```

---

## APIs Externas

### BrasilAPI - Consulta CNPJ

| Método | Endpoint |
|--------|----------|
| GET | `https://brasilapi.com.br/api/cnpj/v1/{cnpj}` |

**Rate Limit:** Não documentado (usar com moderação)

**Campos Retornados:**
- `razao_social`, `nome_fantasia`, `cnpj`
- `email`, `ddd_telefone_1`
- `descricao_tipo_de_logradouro`, `logradouro`, `numero`, `complemento`
- `bairro`, `municipio`, `uf`, `cep`

### ViaCEP - Consulta CEP

| Método | Endpoint |
|--------|----------|
| GET | `https://viacep.com.br/ws/{cep}/json/` |

**Rate Limit:** Não documentado

**Campos Retornados:**
- `logradouro`, `bairro`
- `localidade`, `uf`

---

## Fluxos de Dados

### Fluxo: Criar Orçamento

```
1. Usuário seleciona cliente (ou cadastra novo)
   │
2. Usuário adiciona produtos ao carrinho
   │  └── st.session_state.itens.append(item)
   │
3. Usuário clica "Gerar PDF"
   │
4. Sistema gera número ORS
   │  └── gerar_numero_orcamento()
   │      └── Lê/atualiza sequencia em orcamentos.json
   │
5. Sistema monta dict com dados completos
   │
6. Sistema salva orçamento
   │  └── salvar_orcamento(dados)
   │
7. Sistema gera PDF
   │  └── gerar_pdf_orcamento(dados)
   │      └── PDFOrcamento → bytes
   │
8. Sistema oferece download
   └── st.download_button(data=pdf_bytes)
```

### Fluxo: Editar Orçamento

```
1. Usuário busca orçamento (número ou lista)
   │  └── buscar_orcamento(numero)
   │
2. Usuário clica "Carregar para Edição"
   │  └── Popula st.session_state com dados existentes
   │  └── st.session_state.editando = True
   │  └── st.session_state.numero_orcamento = numero
   │
3. Usuário modifica dados na aba "Criar Orçamento"
   │
4. Usuário clica "Gerar PDF"
   │  └── Usa MESMO número (não gera novo)
   │
5. Sistema sobrescreve orçamento existente
   └── salvar_orcamento() detecta duplicata e atualiza
```

---

## Configurações

### .streamlit/config.toml

```toml
[theme]
# Cor primária (botões, links)
primaryColor = "#E87A2A"

# Cor de fundo principal
backgroundColor = "#1C1C1C"

# Cor de fundo secundária (sidebar, cards)
secondaryBackgroundColor = "#2D2D2D"

# Cor do texto
textColor = "#FAFAFA"

# Fonte
font = "sans serif"
```

### Procfile (Railway)

```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

**Parâmetros:**
- `--server.port $PORT`: Usa porta definida pelo Railway
- `--server.address 0.0.0.0`: Aceita conexões externas
- `--server.headless true`: Desabilita prompts interativos

---

## Deploy e Infraestrutura

### Railway

**Configuração:**
- Runtime: Python 3.10+
- Build: Automático via `requirements.txt`
- Start: Via `Procfile`

**Variáveis de Ambiente:**
- `PORT`: Definida automaticamente pelo Railway

### Cloudflare

**DNS:**
- Tipo: CNAME
- Nome: @ (raiz)
- Target: `*.up.railway.app`
- Proxy: Ativado (SSL automático)

**SSL:**
- Modo: Full
- Certificado: Edge (Cloudflare)

---

## Troubleshooting

### Erro: "Page not found"

**Causa:** `baseUrlPath` configurado incorretamente ou cache do browser.

**Solução:**
1. Verificar `Procfile` não tem `--server.baseUrlPath`
2. Limpar cache do browser (Ctrl+Shift+R)
3. Aguardar redeploy completo

### Erro: "use_container_width" / "use_column_width"

**Causa:** Incompatibilidade de versão do Streamlit.

**Solução:**
- Streamlit < 1.28: usar `use_column_width=True`
- Streamlit >= 1.28: usar `use_container_width=True`

### Erro: "0 is not in iterable"

**Causa:** Selectbox recebendo índice ao invés de valor.

**Solução:**
```python
# Errado
st.session_state.cli_uf = 0

# Correto
st.session_state.cli_uf = "MG"
```

### PDF não gera / erro de fonte

**Causa:** Fonte não encontrada ou caracteres especiais.

**Solução:**
- Usar fontes padrão: Helvetica, Times, Courier
- Evitar acentos em `set_font()`

---

## Changelog

### v1.0.0 (2026-01-29)
- Release inicial
- Geração de orçamentos em PDF
- Cadastro de clientes PJ/PF
- Consulta CNPJ/CEP automática
- Numeração ORS sequencial
- Edição de orçamentos
- Deploy Railway + Cloudflare

---

## Contato

**Desenvolvido por Be Data**
- GEN.IA - Soluções em Automação

---

*Documentação gerada em 29/01/2026*
