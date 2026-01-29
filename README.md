# Sistema de Orcamentos - Brasil UP

Sistema web para geracao de orcamentos de uniformes.

## Instalacao

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso Local

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

## Estrutura

```
orcamentos-brasilup/
├── app.py              # Aplicacao Streamlit
├── gerar_pdf.py        # Geracao de HTML/PDF
├── catalogo.json       # Produtos e precos
├── requirements.txt    # Dependencias
└── README.md
```

## Catalogo de Produtos

Edite `catalogo.json` para adicionar/remover produtos e precos.

## Deploy no Streamlit Cloud

1. Suba para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositorio
4. Deploy!
