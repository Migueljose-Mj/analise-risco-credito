import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página
st.set_page_config(page_title="Análise de Risco de Crédito", layout="wide", page_icon="💳")

# Função para conectar ao banco de dados SQLite
def conectar_banco():
    conn = sqlite3.connect('banco_credito.db')
    return conn

# Criar a tabela se não existir
def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            renda REAL NOT NULL,
            score INTEGER NOT NULL,
            valor_emprestimo REAL NOT NULL,
            num_parcelas INTEGER NOT NULL,
            valor_parcela REAL NOT NULL,
            classificacao_risco TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Regra de negócio para cálculo de risco
def calcular_risco(score, renda, valor_parcela):
    comprometimento_renda = (valor_parcela / renda) * 100 if renda > 0 else 100
    
    if score >= 700 and comprometimento_renda <= 30:
        return "Baixo Risco"
    elif score >= 500 and comprometimento_renda <= 50:
        return "Médio Risco"
    else:
        return "Alto Risco"

# Inicializa o banco ao carregar o script
inicializar_banco()

# --- BARRA LATERAL (Operações CRUD) ---
st.sidebar.header("⚙️ Painel de Operações")
opcao_operacao = st.sidebar.radio(
    "Escolha a Ação:",
    ["➕ Novo Cadastro", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "💣 Zerar Banco"]
)

st.sidebar.markdown("---")

# 1. CREATE (Novo Cadastro)
if opcao_operacao == "➕ Novo Cadastro":
    st.sidebar.subheader("Novo Cadastro")
    nome = st.sidebar.text_input("Nome do Cliente")
    idade = st.sidebar.number_input("Idade", min_value=18, max_value=100, value=25)
    renda = st.sidebar.number_input("Renda Mensal (R$)", min_value=100.0, value=3000.0, step=500.0)
    score = st.sidebar.slider("Score Serasa/SPC", min_value=0, max_value=1000, value=650)

    valor_emprestimo = st.sidebar.number_input("Valor Solicitado (R$)", min_value=500.0, value=10000.0, step=1000.0)
    num_parcelas = st.sidebar.slider("Quantidade de Parcelas", min_value=1, max_value=72, value=12)

    taxa_juros = 0.02
    total_com_juros = valor_emprestimo * (1 + (taxa_juros * num_parcelas))
    valor_parcela = total_com_juros / num_parcelas

    st.sidebar.info(f"**Parcela estimada:** R$ {valor_parcela:.2f}")

    if st.sidebar.button("💾 Cadastrar"):
        if nome.strip() == "":
            st.sidebar.error("Preencha o nome do cliente.")
        else:
            risco = calcular_risco(score, renda, valor_parcela)
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nome, idade, renda, score, valor_emprestimo, num_parcelas, valor_parcela, classificacao_risco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, idade, renda, score, valor_emprestimo, num_parcelas, valor_parcela, risco))
            conn.commit()
            conn.close()
            st.sidebar.success(f"Cliente {nome} cadastrado!")
            st.rerun()

# 2. UPDATE (Editar Cliente via SQL)
elif opcao_operacao == "✏️ Editar Cliente":
    st.sidebar.subheader("Modificar Dados do Cliente")
    conn = conectar_banco()
    ids_df = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    conn.close()

    if not ids_df.empty:
        # Cria lista com ID e Nome para a seleção
        lista_clientes = [f"{row['id']} - {row['nome']}" for _, row in ids_df.iterrows()]
        cliente_selecionado = st.sidebar.selectbox("Selecione o Cliente", lista_clientes)
        id_cliente = int(cliente_selecionado.split(" - ")[0])

        # Buscar dados atuais no banco
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente,))
        dados = cursor.fetchone()
        conn.close()

        novo_score = st.sidebar.slider("Novo Score", 0, 1000, int(dados[4]))
        nova_renda = st.sidebar.number_input("Nova Renda (R$)", min_value=100.0, value=float(dados[3]), step=500.0)
        novo_valor = st.sidebar.number_input("Novo Valor Solicitado (R$)", min_value=500.0, value=float(dados[5]), step=1000.0)

        if st.sidebar.button("🔄 Atualizar Registro"):
            # Recalcular parcela e risco com base nos novos valores
            novas_parcelas = dados[6]
            novo_valor_parcela = (novo_valor * (1 + (0.02 * novas_parcelas))) / novas_parcelas
            novo_risco = calcular_risco(novo_score, nova_renda, novo_valor_parcela)

            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clientes 
                SET score = ?, renda = ?, valor_emprestimo = ?, valor_parcela = ?, classificacao_risco = ?
                WHERE id = ?
            ''', (novo_score, nova_renda, novo_valor, novo_valor_parcela, novo_risco, id_cliente))
            conn.commit()
            conn.close()
            st.sidebar.success("Registro atualizado via UPDATE no banco!")
            st.rerun()
    else:
        st.sidebar.info("Nenhum cliente cadastrado para editar.")

# 3. DELETE (Excluir Registro Específico via SQL)
elif opcao_operacao == "🗑️ Excluir Cliente":
    st.sidebar.subheader("Remover Registro")
    conn = conectar_banco()
    ids_df = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    conn.close()

    if not ids_df.empty:
        lista_clientes = [f"{row['id']} - {row['nome']}" for _, row in ids_df.iterrows()]
        cliente_selecionado = st.sidebar.selectbox("Selecione quem deseja remover", lista_clientes)
        id_cliente = int(cliente_selecionado.split(" - ")[0])

        if st.sidebar.button("❌ Confirmar Exclusão"):
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
            conn.commit()
            conn.close()
            st.sidebar.success("Registro deletado com sucesso!")
            st.rerun()
    else:
        st.sidebar.info("Nenhum cliente cadastrado para excluir.")

# 4. DELETE ALL (Zerar Tabela)
elif opcao_operacao == "💣 Zerar Banco":
    st.sidebar.subheader("Limpeza Completa")
    confirmacao = st.sidebar.checkbox("Confirmar exclusão de TODOS os registros")
    if st.sidebar.button("🗑️ Deletar Tudo"):
        if confirmacao:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes")
            conn.commit()
            conn.close()
            st.sidebar.success("Banco de dados resetado com sucesso!")
            st.rerun()
        else:
            st.sidebar.warning("Marque a caixa de confirmação primeiro.")


# --- PAINEL PRINCIPAL (READ / Dashboard) ---
st.title("💳 Sistema de Análise de Risco de Crédito")
st.markdown("Painel interativo conectado ao banco de dados relacional **SQLite/SQL**.")

conn = conectar_banco()
df = pd.read_sql_query("SELECT * FROM clientes", conn)
conn.close()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Clientes", len(df))
    col2.metric("Total Solicitado", f"R$ {df['valor_emprestimo'].sum():,.2f}")
    col3.metric("Média de Renda", f"R$ {df['renda'].mean():,.2f}")
    col4.metric("Média de Score", f"{int(df['score'].mean())}")

    st.markdown("---")

    col_tabela, col_grafico = st.columns([1.2, 0.8])

    with col_tabela:
        st.subheader("📋 Tabela de Clientes em Tempo Real")
        st.dataframe(
            df[['id', 'nome', 'renda', 'score', 'valor_emprestimo', 'valor_parcela', 'classificacao_risco']],
            use_container_width=True
        )

    with col_grafico:
        st.subheader("📊 Distribuição da Carteira")
        fig, ax = plt.subplots(figsize=(5, 4))
        cores = {"Baixo Risco": "#2ecc71", "Médio Risco": "#f1c40f", "Alto Risco": "#e74c3c"}
        
        contagem_risco = df['classificacao_risco'].value_counts().reset_index()
        contagem_risco.columns = ['Risco', 'Quantidade']
        
        sns.barplot(data=contagem_risco, x='Risco', y='Quantidade', palette=cores, ax=ax)
        ax.set_ylabel("Quantidade de Clientes")
        ax.set_xlabel("")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("Nenhum cliente cadastrado no momento. Use o painel à esquerda para realizar o primeiro cadastro!")
