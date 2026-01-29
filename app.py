"""
Sistema de Geracao de Orcamentos - Brasil UP
"""
import streamlit as st
import json
from datetime import datetime, timedelta
import requests

# Configuracao da pagina
st.set_page_config(
    page_title="SalesFlow by GEN.IA",
    page_icon="⚡",
    layout="wide"
)

# CSS customizado - Paleta Be Data
st.markdown("""
<style>
    /* Botoes primarios - Laranja */
    .stButton > button[kind="primary"] {
        background-color: #E87A2A;
        border-color: #E87A2A;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #C45C26;
        border-color: #C45C26;
    }

    /* Botoes secundarios */
    .stButton > button {
        border-color: #E87A2A;
        color: #E87A2A;
    }
    .stButton > button:hover {
        border-color: #F5A623;
        color: #F5A623;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #F5A623;
        border-color: #F5A623;
        color: #1C1C1C;
    }
    .stDownloadButton > button:hover {
        background-color: #E87A2A;
        border-color: #E87A2A;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #2D2D2D;
        border-bottom-color: #E87A2A;
    }

    /* Dividers */
    hr {
        border-color: #3D3D3D;
    }

    /* Success messages */
    .stSuccess {
        background-color: #2D4A2D;
    }

    /* Info messages */
    .stInfo {
        background-color: #2D3D4A;
    }
</style>
""", unsafe_allow_html=True)

# === FUNCOES DE DADOS ===

@st.cache_data
def carregar_catalogo():
    with open("catalogo.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_catalogo(catalogo):
    with open("catalogo.json", "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

def carregar_clientes():
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Garante que tenha a estrutura correta
            if "pessoas" not in data:
                data["pessoas"] = []
            return data
    except:
        return {"empresas": [], "pessoas": []}

def salvar_clientes(clientes):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=2)

def consultar_cnpj(cnpj: str) -> dict:
    """Consulta CNPJ na BrasilAPI (gratuita)."""
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        return None

    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ: 00.000.000/0000-00"""
    cnpj = "".join(filter(str.isdigit, cnpj))
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def consultar_cep(cep: str) -> dict:
    """Consulta CEP na ViaCEP (gratuita)."""
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        return None
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                return dados
        return None
    except:
        return None

def carregar_orcamentos():
    """Carrega orcamentos salvos."""
    try:
        with open("orcamentos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"orcamentos": [], "sequencia": {}}

def salvar_orcamentos(data):
    """Salva orcamentos."""
    with open("orcamentos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gerar_numero_orcamento():
    """
    Gera numero ORS sequencial: ORS + MM + sequencia (comeca em 100)
    Ex: Janeiro -> ORS01100, ORS01101...
        Fevereiro -> ORS02100, ORS02101...
    """
    data = carregar_orcamentos()
    mes_atual = datetime.now().strftime("%m")  # "01", "02", etc.

    # Pega a sequencia do mes atual (comeca em 100)
    seq = data["sequencia"].get(mes_atual, 99) + 1
    data["sequencia"][mes_atual] = seq
    salvar_orcamentos(data)

    return f"ORS{mes_atual}{seq:03d}"

def salvar_orcamento(dados_orcamento):
    """Salva um orcamento completo."""
    data = carregar_orcamentos()

    # Verifica se ja existe (para edicao)
    existe = False
    for i, orc in enumerate(data["orcamentos"]):
        if orc["numero"] == dados_orcamento["numero"]:
            data["orcamentos"][i] = dados_orcamento
            existe = True
            break

    if not existe:
        data["orcamentos"].append(dados_orcamento)

    salvar_orcamentos(data)

def buscar_orcamento(numero):
    """Busca orcamento pelo numero."""
    data = carregar_orcamentos()
    for orc in data["orcamentos"]:
        if orc["numero"] == numero:
            return orc
    return None

def listar_orcamentos():
    """Lista todos os orcamentos."""
    data = carregar_orcamentos()
    return data["orcamentos"]

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carrega dados
catalogo = carregar_catalogo()
clientes_data = carregar_clientes()

# === INTERFACE ===

# Header centralizado com logo
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image("logo_bedata.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>SalesFlow <span style='color: #E87A2A; font-size: 0.5em;'>by GEN.IA</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; margin-bottom: 20px; font-size: 18px;'>Brasil UP Uniformes Profissionais</p>", unsafe_allow_html=True)

st.divider()

# Inicializa session state
if "itens" not in st.session_state:
    st.session_state.itens = []
if "dados_cnpj" not in st.session_state:
    st.session_state.dados_cnpj = None
if "numero_orcamento" not in st.session_state:
    st.session_state.numero_orcamento = None
if "editando" not in st.session_state:
    st.session_state.editando = False

# Tabs principais
tab_orcamento, tab_editar, tab_clientes, tab_produtos = st.tabs([
    "📋 Criar Orcamento",
    "✏️ Editar Orcamento",
    "🏢 Cadastrar Empresa",
    "⚙️ Cadastrar Produto"
])

# === TAB EDITAR ORCAMENTO ===
with tab_editar:
    st.subheader("✏️ Editar Orcamento Existente")

    # Busca por numero
    col_busca1, col_busca2 = st.columns([3, 1])
    with col_busca1:
        busca_numero = st.text_input("Buscar por numero", placeholder="Ex: ORS01100", key="busca_ors")
    with col_busca2:
        st.write("")
        st.write("")
        btn_buscar = st.button("🔍 Buscar", use_container_width=True)

    orc = None

    # Busca por numero digitado
    if btn_buscar and busca_numero:
        orc = buscar_orcamento(busca_numero.upper().strip())
        if not orc:
            st.error(f"Orcamento '{busca_numero}' nao encontrado.")

    st.divider()

    orcamentos = listar_orcamentos()

    if orcamentos:
        # Lista de orcamentos para selecionar
        opcoes = ["-- Selecione da lista --"] + [
            f"{o['numero']} - {o['cliente']['nome']} ({o['data']})"
            for o in reversed(orcamentos)
        ]

        sel = st.selectbox("Ou selecione da lista", opcoes, key="sel_orcamento_editar")

        if sel != "-- Selecione da lista --":
            numero_sel = sel.split(" - ")[0]
            orc = buscar_orcamento(numero_sel)

    # Mostra detalhes do orcamento selecionado/buscado
    if orc:
        st.success(f"Orcamento encontrado: {orc['numero']}")

        st.markdown(f"""
        **Numero:** {orc['numero']}
        **Cliente:** {orc['cliente']['nome']}
        **Data:** {orc['data']}
        **Total:** {formatar_moeda(orc['total'])}
        **Itens:** {len(orc['itens'])}
        """)

        # Mostra itens
        st.markdown("**Itens do Orcamento:**")
        for item in orc["itens"]:
            st.write(f"• {item['descricao']} - {item['quantidade']:.0f} x {formatar_moeda(item['preco_unitario'])} = {formatar_moeda(item['valor_total'])}")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Carregar para Edicao", type="primary", use_container_width=True, key="btn_editar_orc"):
                # Carrega dados no session state
                st.session_state.numero_orcamento = orc["numero"]
                st.session_state.editando = True
                st.session_state.itens = orc["itens"].copy()

                # Carrega dados do cliente
                st.session_state.cli_nome = orc["cliente"]["nome"]
                st.session_state.cli_contato = orc["cliente"].get("contato", "")
                st.session_state.cli_end = orc["cliente"].get("endereco", "")
                st.session_state.cli_cidade = orc["cliente"].get("cidade", "")
                st.session_state.cli_cep = orc["cliente"].get("cep", "")
                st.session_state.cli_cnpj = orc["cliente"].get("cnpj", "")

                # UF
                ufs = ["MG", "SP", "RJ", "ES", "BA", "GO", "DF", "PR", "SC", "RS", "Outro"]
                uf_orc = orc["cliente"].get("estado", "MG")
                st.session_state.cli_uf = ufs.index(uf_orc) if uf_orc in ufs else 0

                # Carrega observacoes
                st.session_state.obs_orcamento = orc.get("observacoes", "")

                st.toast(f"Orcamento {orc['numero']} carregado!")
                st.info("👆 Agora va para a aba **'Criar Orcamento'** para editar e gerar novo PDF.")

        with col2:
            # Gerar PDF direto
            from gerar_pdf import gerar_pdf_orcamento
            try:
                pdf_bytes = gerar_pdf_orcamento(orc)
                st.download_button(
                    label="📄 Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"Cotacao_{orc['numero']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro: {e}")

    elif not orcamentos:
        st.info("Nenhum orcamento salvo ainda. Crie um orcamento na aba 'Criar Orcamento'.")

# === TAB CADASTRO DE CLIENTES ===
with tab_clientes:
    tipo_cliente = st.radio("Tipo de Cliente", ["🏢 Pessoa Juridica (PJ)", "👤 Pessoa Fisica (PF)"], horizontal=True, key="tipo_cliente")

    if tipo_cliente == "🏢 Pessoa Juridica (PJ)":
        # === CADASTRO PJ ===
        st.subheader("🏢 Cadastrar Empresa")

        col1, col2 = st.columns([2, 1])
        with col1:
            cnpj_input = st.text_input("CNPJ", placeholder="00.000.000/0000-00", key="cnpj_consulta")
        with col2:
            st.write("")
            st.write("")
            btn_consultar = st.button("🔍 Consultar CNPJ", use_container_width=True)

        if btn_consultar and cnpj_input:
            with st.spinner("Consultando CNPJ na Receita Federal..."):
                dados = consultar_cnpj(cnpj_input)
                if dados:
                    st.session_state.dados_cnpj = dados
                    st.session_state.emp_razao = dados.get("razao_social", "")
                    st.session_state.emp_fantasia = dados.get("nome_fantasia", "")
                    st.session_state.emp_cnpj = formatar_cnpj(dados.get("cnpj", ""))
                    st.session_state.emp_email = dados.get("email", "") or ""
                    st.session_state.emp_telefone = dados.get("ddd_telefone_1", "") or ""
                    logradouro = f"{dados.get('descricao_tipo_de_logradouro', '')} {dados.get('logradouro', '')}".strip()
                    st.session_state.emp_log = logradouro
                    st.session_state.emp_num = dados.get("numero", "") or ""
                    st.session_state.emp_comp = dados.get("complemento", "") or ""
                    st.session_state.emp_bairro = dados.get("bairro", "") or ""
                    st.session_state.emp_cidade = dados.get("municipio", "") or ""
                    st.session_state.emp_uf = dados.get("uf", "") or ""
                    st.session_state.emp_cep = str(dados.get("cep", "")) if dados.get("cep") else ""
                    st.success("CNPJ encontrado!")
                    st.rerun()
                else:
                    st.error("CNPJ nao encontrado ou invalido.")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            emp_razao = st.text_input("Razao Social *", key="emp_razao")
            emp_fantasia = st.text_input("Nome Fantasia", key="emp_fantasia")
            emp_cnpj = st.text_input("CNPJ", key="emp_cnpj")
        with col2:
            emp_email = st.text_input("E-mail", key="emp_email")
            emp_telefone = st.text_input("Telefone", key="emp_telefone")
            emp_ie = st.text_input("Inscricao Estadual", key="emp_ie")

        st.markdown("**Endereco**")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            emp_logradouro = st.text_input("Logradouro", key="emp_log")
        with col2:
            emp_numero = st.text_input("Numero", key="emp_num")
        with col3:
            emp_complemento = st.text_input("Complemento", key="emp_comp")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            emp_bairro = st.text_input("Bairro", key="emp_bairro")
        with col2:
            emp_cidade = st.text_input("Cidade", key="emp_cidade")
        with col3:
            emp_uf = st.text_input("UF", key="emp_uf", max_chars=2)
        with col4:
            emp_cep = st.text_input("CEP", key="emp_cep")

        st.divider()
        st.markdown("**👤 Contato Principal**")

        col1, col2 = st.columns(2)
        with col1:
            contato_nome = st.text_input("Nome do Contato *", key="cont_nome")
            contato_cargo = st.text_input("Cargo", key="cont_cargo")
        with col2:
            contato_email = st.text_input("E-mail do Contato", key="cont_email")
            contato_telefone = st.text_input("Telefone do Contato", key="cont_tel")

        st.divider()

        if st.button("💾 Salvar Empresa", use_container_width=True, type="primary"):
            if emp_razao and contato_nome:
                nova_empresa = {
                    "id": len(clientes_data["empresas"]) + 1,
                    "tipo": "PJ",
                    "razao_social": emp_razao,
                    "nome_fantasia": emp_fantasia,
                    "cnpj": emp_cnpj,
                    "ie": emp_ie,
                    "email": emp_email,
                    "telefone": emp_telefone,
                    "endereco": {
                        "logradouro": emp_logradouro,
                        "numero": emp_numero,
                        "complemento": emp_complemento,
                        "bairro": emp_bairro,
                        "cidade": emp_cidade,
                        "uf": emp_uf,
                        "cep": emp_cep
                    },
                    "contatos": [{
                        "nome": contato_nome,
                        "cargo": contato_cargo,
                        "email": contato_email,
                        "telefone": contato_telefone
                    }],
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                clientes_data["empresas"].append(nova_empresa)
                salvar_clientes(clientes_data)
                st.success(f"Empresa '{emp_razao}' cadastrada!")
                st.session_state.dados_cnpj = None
                for key in ["emp_razao", "emp_fantasia", "emp_cnpj", "emp_email", "emp_telefone",
                            "emp_ie", "emp_log", "emp_num", "emp_comp", "emp_bairro",
                            "emp_cidade", "emp_uf", "emp_cep", "cont_nome", "cont_cargo",
                            "cont_email", "cont_tel", "cnpj_consulta"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            else:
                st.error("Preencha a Razao Social e o Nome do Contato.")

    else:
        # === CADASTRO PF ===
        st.subheader("👤 Cadastrar Pessoa Fisica")

        col1, col2 = st.columns(2)
        with col1:
            pf_nome = st.text_input("Nome Completo *", key="pf_nome")
            pf_cpf = st.text_input("CPF", placeholder="000.000.000-00", key="pf_cpf")
            pf_rg = st.text_input("RG", key="pf_rg")
        with col2:
            pf_email = st.text_input("E-mail", key="pf_email")
            pf_telefone = st.text_input("Telefone *", key="pf_telefone")
            pf_whatsapp = st.text_input("WhatsApp", key="pf_whatsapp")

        st.markdown("**Endereco**")

        # Consulta CEP
        col1, col2 = st.columns([2, 1])
        with col1:
            pf_cep = st.text_input("CEP", placeholder="00000-000", key="pf_cep")
        with col2:
            st.write("")
            st.write("")
            btn_cep = st.button("🔍 Buscar CEP", use_container_width=True, key="btn_cep")

        if btn_cep and pf_cep:
            with st.spinner("Buscando endereco..."):
                dados_cep = consultar_cep(pf_cep)
                if dados_cep:
                    st.session_state.pf_log = dados_cep.get("logradouro", "")
                    st.session_state.pf_bairro = dados_cep.get("bairro", "")
                    st.session_state.pf_cidade = dados_cep.get("localidade", "")
                    st.session_state.pf_uf = dados_cep.get("uf", "")
                    st.success("Endereco encontrado!")
                    st.rerun()
                else:
                    st.error("CEP nao encontrado.")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            pf_logradouro = st.text_input("Logradouro", key="pf_log")
        with col2:
            pf_numero = st.text_input("Numero", key="pf_num")
        with col3:
            pf_complemento = st.text_input("Complemento", key="pf_comp")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            pf_bairro = st.text_input("Bairro", key="pf_bairro")
        with col2:
            pf_cidade = st.text_input("Cidade", key="pf_cidade")
        with col3:
            pf_uf = st.text_input("UF", key="pf_uf", max_chars=2)

        st.divider()

        if st.button("💾 Salvar Cliente PF", use_container_width=True, type="primary"):
            if pf_nome and pf_telefone:
                nova_pessoa = {
                    "id": len(clientes_data.get("pessoas", [])) + 1,
                    "tipo": "PF",
                    "nome": pf_nome,
                    "cpf": pf_cpf,
                    "rg": pf_rg,
                    "email": pf_email,
                    "telefone": pf_telefone,
                    "whatsapp": pf_whatsapp,
                    "endereco": {
                        "logradouro": pf_logradouro,
                        "numero": pf_numero,
                        "complemento": pf_complemento,
                        "bairro": pf_bairro,
                        "cidade": pf_cidade,
                        "uf": pf_uf,
                        "cep": pf_cep
                    },
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if "pessoas" not in clientes_data:
                    clientes_data["pessoas"] = []
                clientes_data["pessoas"].append(nova_pessoa)
                salvar_clientes(clientes_data)
                st.success(f"Cliente '{pf_nome}' cadastrado!")
                for key in ["pf_nome", "pf_cpf", "pf_rg", "pf_email", "pf_telefone",
                            "pf_whatsapp", "pf_log", "pf_num", "pf_comp", "pf_bairro",
                            "pf_cidade", "pf_uf", "pf_cep"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            else:
                st.error("Preencha o Nome e Telefone.")

    # === LISTA DE CLIENTES CADASTRADOS ===
    st.divider()
    st.subheader("📋 Clientes Cadastrados")

    # Empresas (PJ)
    if clientes_data["empresas"]:
        for emp in clientes_data["empresas"]:
            with st.expander(f"🏢 {emp['razao_social']} - {emp.get('cnpj', 'Sem CNPJ')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nome Fantasia:** {emp.get('nome_fantasia', '-')}")
                    st.write(f"**E-mail:** {emp.get('email', '-')}")
                    st.write(f"**Telefone:** {emp.get('telefone', '-')}")
                with col2:
                    end = emp.get("endereco", {})
                    st.write(f"**Endereco:** {end.get('logradouro', '')}, {end.get('numero', '')}")
                    st.write(f"**Cidade:** {end.get('cidade', '')} - {end.get('uf', '')}")
                st.markdown("**Contatos:**")
                for cont in emp.get("contatos", []):
                    st.write(f"- {cont['nome']} ({cont.get('cargo', '-')}) - {cont.get('telefone', '')}")

    # Pessoas (PF)
    if clientes_data.get("pessoas"):
        for pf in clientes_data["pessoas"]:
            with st.expander(f"👤 {pf['nome']} - {pf.get('cpf', 'Sem CPF')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**CPF:** {pf.get('cpf', '-')}")
                    st.write(f"**E-mail:** {pf.get('email', '-')}")
                    st.write(f"**Telefone:** {pf.get('telefone', '-')}")
                with col2:
                    end = pf.get("endereco", {})
                    st.write(f"**Endereco:** {end.get('logradouro', '')}, {end.get('numero', '')}")
                    st.write(f"**Cidade:** {end.get('cidade', '')} - {end.get('uf', '')}")

    if not clientes_data["empresas"] and not clientes_data.get("pessoas"):
        st.info("Nenhum cliente cadastrado ainda.")

# === TAB CADASTRO DE PRODUTOS ===
with tab_produtos:
    st.subheader("Cadastrar Novo Produto")

    col1, col2 = st.columns(2)
    with col1:
        nova_categoria = st.text_input("Categoria", placeholder="Ex: Camisas, Calcas, Jalecos...", key="nova_cat")
        novo_nome = st.text_input("Nome do Produto", placeholder="Ex: CAMISA POLO MANGA CURTA", key="novo_nome")
    with col2:
        novo_preco = st.number_input("Preco Padrao (R$)", min_value=0.0, value=50.0, format="%.2f", key="novo_preco")

    if st.button("💾 Salvar Produto", use_container_width=True, key="btn_salvar_prod"):
        if nova_categoria and novo_nome:
            novo_produto = {
                "categoria": nova_categoria,
                "nome": novo_nome.upper(),
                "preco": novo_preco
            }
            catalogo["produtos"].append(novo_produto)
            salvar_catalogo(catalogo)
            st.success(f"Produto '{novo_nome}' cadastrado com sucesso!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Preencha categoria e nome do produto.")

    st.divider()
    st.subheader("Produtos Cadastrados")

    categorias_prod = sorted(set(p["categoria"] for p in catalogo["produtos"]))
    for cat in categorias_prod:
        with st.expander(f"📁 {cat}"):
            produtos_cat = [p for p in catalogo["produtos"] if p["categoria"] == cat]
            for p in produtos_cat:
                st.write(f"• {p['nome']} - {formatar_moeda(p['preco'])}")

# === TAB ORCAMENTO ===

# Callback para preencher campos quando cliente é selecionado
def preencher_dados_cliente():
    cliente_sel = st.session_state.sel_cliente
    if cliente_sel == "-- Novo Cliente --":
        for key in ["cli_nome", "cli_contato", "cli_end", "cli_cidade", "cli_cep", "cli_cnpj"]:
            if key in st.session_state:
                st.session_state[key] = ""
        st.session_state.cli_uf = 0
    else:
        clientes = carregar_clientes()
        # Tenta encontrar em empresas (PJ)
        emp = next((e for e in clientes["empresas"] if f"🏢 {e['razao_social']}" == cliente_sel), None)
        if emp:
            st.session_state.cli_nome = emp.get("razao_social", "")
            contatos = emp.get("contatos", [])
            st.session_state.cli_contato = contatos[0]["nome"] if contatos else ""
            end = emp.get("endereco", {})
            logr = end.get("logradouro", "")
            num = end.get("numero", "")
            st.session_state.cli_end = f"{logr}, {num}".strip(", ") if logr or num else ""
            st.session_state.cli_cidade = end.get("cidade", "")
            st.session_state.cli_cep = end.get("cep", "")
            st.session_state.cli_cnpj = emp.get("cnpj", "")
            ufs = ["MG", "SP", "RJ", "ES", "BA", "GO", "DF", "PR", "SC", "RS", "Outro"]
            uf_emp = end.get("uf", "MG")
            st.session_state.cli_uf = ufs.index(uf_emp) if uf_emp in ufs else 0
        else:
            # Tenta encontrar em pessoas (PF)
            pf = next((p for p in clientes.get("pessoas", []) if f"👤 {p['nome']}" == cliente_sel), None)
            if pf:
                st.session_state.cli_nome = pf.get("nome", "")
                st.session_state.cli_contato = ""
                end = pf.get("endereco", {})
                logr = end.get("logradouro", "")
                num = end.get("numero", "")
                st.session_state.cli_end = f"{logr}, {num}".strip(", ") if logr or num else ""
                st.session_state.cli_cidade = end.get("cidade", "")
                st.session_state.cli_cep = end.get("cep", "")
                st.session_state.cli_cnpj = pf.get("cpf", "")
                ufs = ["MG", "SP", "RJ", "ES", "BA", "GO", "DF", "PR", "SC", "RS", "Outro"]
                uf_pf = end.get("uf", "MG")
                st.session_state.cli_uf = ufs.index(uf_pf) if uf_pf in ufs else 0

with tab_orcamento:
    col_form, col_preview = st.columns([1, 1])

    with col_form:
        st.subheader("📋 Dados do Cliente")

        # Recarrega clientes (pode ter sido atualizado)
        clientes_data = carregar_clientes()

        # Monta lista de clientes (PJ + PF)
        lista_clientes = ["-- Novo Cliente --"]
        lista_clientes += [f"🏢 {e['razao_social']}" for e in clientes_data["empresas"]]
        lista_clientes += [f"👤 {p['nome']}" for p in clientes_data.get("pessoas", [])]

        cliente_selecionado = st.selectbox(
            "Selecionar Cliente Cadastrado",
            lista_clientes,
            key="sel_cliente",
            on_change=preencher_dados_cliente
        )

        cliente_nome = st.text_input("Nome / Razao Social *", key="cli_nome")
        cliente_contato = st.text_input("Contato", key="cli_contato")
        cliente_endereco = st.text_input("Endereco", key="cli_end")

        col1, col2 = st.columns(2)
        with col1:
            cliente_cidade = st.text_input("Cidade", key="cli_cidade")
            cliente_cep = st.text_input("CEP", key="cli_cep")
        with col2:
            ufs = ["MG", "SP", "RJ", "ES", "BA", "GO", "DF", "PR", "SC", "RS", "Outro"]
            cliente_estado = st.selectbox("Estado", ufs, key="cli_uf")
            cliente_cnpj = st.text_input("CPF/CNPJ", key="cli_cnpj")

        st.divider()
        st.subheader("📝 Dados do Orcamento")

        col1, col2 = st.columns(2)
        with col1:
            vendedor = st.selectbox("Vendedor", catalogo["vendedores"], key="vendedor")
            data_orcamento = st.date_input("Data", datetime.now(), key="data_orc")
        with col2:
            validade_dias = st.number_input("Validade (dias)", value=catalogo["validade_dias"], min_value=1, key="validade")
            data_expiracao = data_orcamento + timedelta(days=validade_dias)
            st.text_input("Expiracao", value=data_expiracao.strftime("%d/%m/%Y"), disabled=True, key="exp")

        st.divider()
        st.subheader("🛒 Adicionar Produtos")

        modo_adicao = st.radio("Modo", ["Catalogo", "Produto Avulso"], horizontal=True, key="modo")

        if modo_adicao == "Catalogo":
            categorias = sorted(set(p["categoria"] for p in catalogo["produtos"]))
            categoria_sel = st.selectbox("Categoria", categorias, key="cat_sel")

            produtos_cat = [p for p in catalogo["produtos"] if p["categoria"] == categoria_sel]
            produto_nomes = [p["nome"] for p in produtos_cat]
            produto_sel = st.selectbox("Produto", produto_nomes, key="prod_sel")

            produto_dados = next((p for p in produtos_cat if p["nome"] == produto_sel), None)

            if produto_dados:
                col1, col2, col3 = st.columns(3)
                with col1:
                    tamanho_sel = st.text_input("Tamanho", value="M", key="tam_sel")
                with col2:
                    quantidade = st.number_input("Quantidade", value=1, min_value=1, key="qtd")
                with col3:
                    preco_unit = st.number_input(
                        "Preco Unitario (R$)",
                        value=produto_dados["preco"],
                        format="%.2f",
                        key="preco_unit",
                        help="Altere se necessario"
                    )

                descricao_final = f"{produto_sel} {tamanho_sel}"

        else:
            col1, col2 = st.columns(2)
            with col1:
                descricao_final = st.text_input("Descricao do Produto", key="desc_avulso").upper()
            with col2:
                tamanho_sel = st.text_input("Tamanho", value="", key="tam_avulso")

            if tamanho_sel:
                descricao_final = f"{descricao_final} {tamanho_sel}"

            col1, col2 = st.columns(2)
            with col1:
                quantidade = st.number_input("Quantidade", value=1, min_value=1, key="qtd_avulso")
            with col2:
                preco_unit = st.number_input("Preco Unitario (R$)", value=50.0, format="%.2f", key="preco_avulso")

        if st.button("➕ Adicionar Item", use_container_width=True, key="btn_add"):
            if descricao_final and quantidade > 0 and preco_unit > 0:
                item = {
                    "descricao": descricao_final,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unit,
                    "valor_total": quantidade * preco_unit
                }
                st.session_state.itens.append(item)
                st.success(f"Item adicionado: {item['descricao']}")
                st.rerun()
            else:
                st.error("Preencha todos os campos.")

        st.divider()
        st.subheader("📝 Informacoes Importantes")
        observacoes = st.text_area(
            "Observacoes do Orcamento",
            placeholder="Ex: Frete por conta do cliente. Prazo de entrega: 15 dias uteis. Pagamento: 50% entrada + 50% na entrega.",
            height=100,
            key="obs_orcamento"
        )

    with col_preview:
        st.subheader("👁️ Preview do Orcamento")

        # Usa numero existente (edicao) ou gera novo
        if st.session_state.numero_orcamento and st.session_state.editando:
            numero_orcamento = st.session_state.numero_orcamento
        else:
            if "numero_orcamento_novo" not in st.session_state:
                st.session_state.numero_orcamento_novo = gerar_numero_orcamento()
            numero_orcamento = st.session_state.numero_orcamento_novo

        st.markdown(f"""
        **Cotacao n°** {numero_orcamento}
        **Data:** {data_orcamento.strftime("%d/%m/%Y")}
        **Expiracao:** {data_expiracao.strftime("%d/%m/%Y")}
        **Vendedor:** {vendedor}
        """)

        if cliente_nome:
            st.markdown(f"""
            ---
            **Cliente:** {cliente_nome}
            {cliente_endereco}
            {cliente_cidade} {cliente_estado} {cliente_cep}
            **CPF/CNPJ:** {cliente_cnpj}
            """)

        st.markdown("---")

        if st.session_state.itens:
            st.markdown("**Itens:**")

            total = 0
            for i, item in enumerate(st.session_state.itens):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
                with col1:
                    st.text(item["descricao"])
                with col2:
                    st.text(f"{item['quantidade']:.0f} Un")
                with col3:
                    st.text(formatar_moeda(item["valor_total"]))
                with col4:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.itens.pop(i)
                        st.rerun()
                total += item["valor_total"]

            st.markdown("---")
            st.markdown(f"### Total: {formatar_moeda(total)}")

            if observacoes:
                st.markdown("---")
                st.warning(f"**Informacoes Importantes:**\n\n{observacoes}")

            st.divider()

            if st.button("📄 Gerar PDF", type="primary", use_container_width=True):
                dados_orcamento = {
                    "numero": numero_orcamento,
                    "data": data_orcamento.strftime("%d/%m/%Y"),
                    "data_iso": data_orcamento.strftime("%Y-%m-%d"),
                    "expiracao": data_expiracao.strftime("%d/%m/%Y"),
                    "vendedor": vendedor,
                    "cliente": {
                        "nome": cliente_nome,
                        "contato": cliente_contato,
                        "endereco": cliente_endereco,
                        "cidade": cliente_cidade,
                        "estado": cliente_estado,
                        "cep": cliente_cep,
                        "cnpj": cliente_cnpj
                    },
                    "itens": st.session_state.itens.copy(),
                    "total": total,
                    "empresa": catalogo["empresa"],
                    "observacoes": observacoes
                }

                # Salva o orcamento
                salvar_orcamento(dados_orcamento)

                from gerar_pdf import gerar_pdf_orcamento

                try:
                    pdf_bytes = gerar_pdf_orcamento(dados_orcamento)
                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=pdf_bytes,
                        file_name=f"Cotacao_{numero_orcamento}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success(f"Orcamento {numero_orcamento} salvo!")
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")
        else:
            st.info("Adicione produtos ao orcamento.")

    st.divider()
    if st.button("🗑️ Limpar Orcamento", use_container_width=True):
        st.session_state.itens = []
        st.session_state.numero_orcamento = None
        st.session_state.editando = False
        if "numero_orcamento_novo" in st.session_state:
            del st.session_state.numero_orcamento_novo
        st.rerun()

# === RODAPE ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #666;">
    <p style="margin: 5px 0;"><strong style="color: #E87A2A;">SalesFlow</strong> by GEN.IA</p>
    <p style="margin: 5px 0; font-size: 12px;">Desenvolvido por <strong>Be Data</strong> | Automacoes e Inteligencia de Dados</p>
</div>
""", unsafe_allow_html=True)
