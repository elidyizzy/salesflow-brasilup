"""
Geracao de PDF para orcamentos usando fpdf2.
Layout profissional Brasil UP.
"""

import os
from fpdf import FPDF


def formatar_moeda(valor):
    """Formata valor em reais."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class PDFOrcamento(FPDF):
    def __init__(self, dados):
        super().__init__()
        self.dados = dados
        self.set_auto_page_break(auto=True, margin=30)

    def header(self):
        # Fundo do header (aumentado para caber a logo)
        self.set_fill_color(232, 244, 252)
        self.rect(0, 0, 210, 42, 'F')

        # Linha azul inferior
        self.set_fill_color(30, 90, 138)
        self.rect(0, 42, 210, 2, 'F')

        # Logo (direita) - tenta carregar imagem
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        if os.path.exists(logo_path):
            # Logo: 3230x1291 px (proporcao ~2.5:1)
            # w=50mm -> h=20mm
            self.image(logo_path, x=145, y=8, w=50)
        else:
            # Fallback: texto
            self.set_font('Helvetica', 'B', 22)
            self.set_xy(145, 14)
            self.set_text_color(30, 90, 138)
            self.cell(25, 8, 'Brasil', align='R')
            self.set_text_color(245, 158, 11)
            self.cell(20, 8, 'UP', align='L')

        # Slogan (esquerda, centralizado verticalmente)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 90, 138)
        self.set_xy(15, 18)
        self.cell(100, 6, self.dados['empresa']['slogan'], align='L')

    def footer(self):
        self.set_y(-25)
        self.set_fill_color(248, 250, 252)
        self.rect(0, self.get_y(), 210, 30, 'F')
        self.set_draw_color(226, 232, 240)
        self.line(0, self.get_y(), 210, self.get_y())

        # Site
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(30, 90, 138)
        self.set_xy(0, -22)
        self.cell(0, 4, self.dados['empresa']['site'], align='C')

        # Email
        self.set_font('Helvetica', '', 8)
        self.set_text_color(75, 85, 99)
        self.set_xy(0, -17)
        self.cell(0, 4, 'relacionamento@brasiluniformes.com', align='C')

        # Endereco
        self.set_xy(0, -13)
        self.cell(0, 4, 'R. Nossa Sra. das Gracas, 96A - Vila das Flores, Betim - MG, 32605-160', align='C')

        # Pagina
        self.set_xy(0, -8)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(156, 163, 175)
        self.cell(0, 4, f'Pagina {self.page_no()}', align='C')


def gerar_pdf_orcamento(dados: dict) -> bytes:
    """
    Gera PDF do orcamento no formato Brasil UP.
    Retorna bytes do PDF.
    """
    pdf = PDFOrcamento(dados)
    pdf.add_page()

    # === CLIENTE E NUMERO DA COTACAO ===
    y_start = 52  # Ajustado para novo header

    # Numero cotacao (direita, no topo)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 90, 138)
    pdf.set_xy(15, y_start)
    pdf.cell(180, 8, f"Cotacao n. {dados['numero']}", align='R')

    # Cliente (esquerda)
    pdf.set_xy(15, y_start)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(100, 6, dados['cliente']['nome'], align='L')

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(75, 85, 99)

    pdf.set_xy(15, y_start + 7)
    pdf.cell(100, 5, dados['cliente']['endereco'], align='L')

    pdf.set_xy(15, y_start + 12)
    pdf.cell(100, 5, f"{dados['cliente']['cidade']} {dados['cliente']['estado']}", align='L')

    pdf.set_xy(15, y_start + 17)
    pdf.cell(100, 5, dados['cliente']['cep'], align='L')

    pdf.set_xy(15, y_start + 22)
    pdf.cell(100, 5, 'Brasil', align='L')

    pdf.set_xy(15, y_start + 28)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(20, 5, 'CPF/CNPJ:', align='L')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(80, 5, dados['cliente']['cnpj'], align='L')

    # === INFO BOX ===
    pdf.set_y(y_start + 40)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(15, pdf.get_y(), 180, 16, 'FD')

    y_box = pdf.get_y() + 2

    # Data
    pdf.set_xy(20, y_box)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(55, 4, 'DATA DA COTACAO', align='L')

    pdf.set_xy(20, y_box + 5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(55, 5, dados['data'], align='L')

    # Expiracao
    pdf.set_xy(80, y_box)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(55, 4, 'EXPIRACAO', align='L')

    pdf.set_xy(80, y_box + 5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(55, 5, dados['expiracao'], align='L')

    # Vendedor
    pdf.set_xy(140, y_box)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(50, 4, 'VENDEDOR', align='L')

    pdf.set_xy(140, y_box + 5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(50, 5, dados['vendedor'], align='L')

    # === TABELA DE ITENS ===
    pdf.set_y(y_start + 58)

    # Header da tabela
    pdf.set_fill_color(30, 90, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)

    pdf.set_x(15)
    pdf.cell(80, 9, '  DESCRICAO', fill=True, align='L')
    pdf.cell(30, 9, 'QUANTIDADE', fill=True, align='C')
    pdf.cell(35, 9, 'PRECO UNIT.', fill=True, align='C')
    pdf.cell(35, 9, 'VALOR', fill=True, align='C')
    pdf.ln()

    # Itens
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(55, 65, 81)

    for i, item in enumerate(dados['itens']):
        bg = (248, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)

        pdf.set_x(15)
        pdf.cell(80, 9, f"  {item['descricao']}", fill=True, align='L')
        pdf.cell(30, 9, f"{item['quantidade']:.0f} Un", fill=True, align='C')
        pdf.cell(35, 9, formatar_moeda(item['preco_unitario']), fill=True, align='C')
        pdf.cell(35, 9, formatar_moeda(item['valor_total']), fill=True, align='C')
        pdf.ln()

    # Linha total
    pdf.set_fill_color(30, 90, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_x(15)
    pdf.cell(145, 11, 'TOTAL', fill=True, align='R')
    pdf.cell(35, 11, formatar_moeda(dados['total']), fill=True, align='C')
    pdf.ln()

    # Observacoes / Informacoes Importantes
    observacoes = dados.get('observacoes', '')
    if observacoes:
        pdf.ln(8)
        pdf.set_fill_color(255, 251, 235)
        pdf.set_draw_color(245, 158, 11)
        pdf.set_text_color(146, 64, 14)

        pdf.set_x(15)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(180, 7, '  INFORMACOES IMPORTANTES', fill=True, border='LTR', align='L')
        pdf.ln()

        pdf.set_font('Helvetica', '', 8)
        pdf.set_x(15)
        pdf.multi_cell(180, 5, f"  {observacoes}", border='LBR', fill=True, align='L')

    return bytes(pdf.output())


if __name__ == "__main__":
    # Teste
    dados_teste = {
        "numero": "ORS00001",
        "data": "28/01/2026",
        "expiracao": "27/02/2026",
        "vendedor": "Elidy Izidio",
        "cliente": {
            "nome": "EMPRESA TESTE LTDA",
            "endereco": "Rua Teste, 123",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "cep": "30000-000",
            "cnpj": "12.345.678/0001-90"
        },
        "itens": [
            {"descricao": "CAMISA OPERACIONAL G", "quantidade": 10, "preco_unitario": 67.90, "valor_total": 679.00},
            {"descricao": "CALCA OPERACIONAL 42", "quantidade": 10, "preco_unitario": 63.90, "valor_total": 639.00}
        ],
        "total": 1318.00,
        "empresa": {
            "nome": "BRASIL UP UNIFORMES PROFISSIONAIS LTDA",
            "endereco": "Av. DOIS 108 | BETIM MG",
            "slogan": "UNIFORMES QUE MOVEM O BRASIL",
            "site": "www.brasiluniformesprofissionais.com"
        },
        "observacoes": "Frete por conta do cliente. Prazo de entrega: 15 dias uteis."
    }

    pdf_bytes = gerar_pdf_orcamento(dados_teste)
    with open("teste_orcamento.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF gerado: teste_orcamento.pdf")
