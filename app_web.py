import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Análise de Risco de Crédito", page_icon="💳", layout="wide"
)


# --- BANCO DE DADOS ---
def conectar_banco():
  conn = sqlite3.connect("risco_credito.db")
  cursor = conn.cursor()

  cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        renda_mensal REAL,
        score_serasa INTEGER
    )""")
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS emprestimos (
        emprestimo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        valor_contratado REAL,
        qtd_parcelas INTEGER,
        data_contratacao DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )""")
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        pagamento_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emprestimo_id INTEGER,
        numero_parcela INTEGER,
        data_vencimento DATE,
        data_pagamento DATE,
        status TEXT,
        FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(emprestimo_id)
    )""")
  conn.commit()
  return conn


# --- QUERY SQL DE RISCO DE CRÉDITO ---
def carregar_dados():
  conn = conectar_banco()
  query = """
    SELECT 
        c.cliente_id AS ID,
        c.nome AS Cliente,
        c.renda_mensal AS Renda,
        c.score_serasa AS Score,
        e.valor_contratado AS Valor_Emprestimo,
        e.qtd_parcelas AS Parcelas,
        SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) AS Qtd_Atrasos,
        
        CASE 
            WHEN SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) >= 2 OR c.score_serasa < 400 
                THEN 'Alto Risco (Inadimplente)'
            WHEN SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) = 1 OR c.score_serasa BETWEEN 400 AND 600 
                THEN 'Médio Risco (Atenção)'
            ELSE 'Baixo Risco (Bom Pagador)'
        END AS Classificacao_Risco

    FROM clientes c
    LEFT JOIN emprestimos e ON c.cliente_id = e.cliente_id
    LEFT JOIN pagamentos p ON e.emprestimo_id = p.emprestimo_id
    GROUP BY c.cliente_id, e.emprestimo_id;
    """
  df = pd.read_sql_query(query, conn)
  conn.close()
  return df


# --- INTERFACE ---
st.title("💳 Sistema de Análise de Risco de Crédito")
st.markdown(
    "Aplicação web para cadastro de clientes, simulação e classificação de"
    " risco em tempo real."
)

aba_cadastro, aba_dashboard = st.tabs(
    ["📥 Novo Cadastro e Simulação", "📊 Painel da Carteira (SQL)"]
)

# ABA 1: FORMULÁRIO
with aba_cadastro:
  st.subheader("Cadastrar Cliente e Empréstimo")

  col1, col2 = st.columns(2)

  with col1:
    nome = st.text_input("Nome do Cliente", placeholder="Ex: Miguel José")
    idade = st.number_input("Idade", min_value=18, max_value=100, value=25)
    renda = st.number_input(
        "Renda Mensal (R$)", min_value=0.0, value=3500.0, step=100.0
    )

  with col2:
    score = st.slider("Score Serasa", min_value=0, max_value=1000, value=650)
    valor = st.number_input(
        "Valor do Empréstimo (R$)", min_value=500.0, value=8000.0, step=500.0
    )
    parcelas = st.selectbox("Quantidade de Parcelas", [6, 12, 18, 24, 36, 48])

  if st.button("💾 Salvar Cadastro e Analisar Risco", type="primary"):
    if nome.strip() == "":
      st.error("Por favor, preencha o nome do cliente!")
    else:
      conn = conectar_banco()
      cursor = conn.cursor()

      cursor.execute(
          """
                INSERT INTO clientes (nome, idade, renda_mensal, score_serasa)
                VALUES (?, ?, ?, ?)
            """,
          (nome, idade, renda, score),
      )
      novo_id = cursor.lastrowid

      cursor.execute(
          """
                INSERT INTO emprestimos (cliente_id, valor_contratado, qtd_parcelas, data_contratacao)
                VALUES (?, ?, ?, DATE('now'))
            """,
          (novo_id, valor, parcelas),
      )

      conn.commit()
      conn.close()

      st.success(f"✅ Cliente **{nome}** cadastrado com sucesso!")
      st.rerun()

# ABA 2: PAINEL E GRÁFICO
with aba_dashboard:
  df = carregar_dados()

  st.subheader("📊 Tabela de Clientes e Risco Calculado")
  st.dataframe(df, use_container_width=True)

  st.divider()

  if not df.empty and "Classificacao_Risco" in df.columns:
    st.subheader("📈 Distribuição do Risco da Carteira")

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = {
        "Baixo Risco (Bom Pagador)": "#4CAF50",
        "Médio Risco (Atenção)": "#FFC107",
        "Alto Risco (Inadimplente)": "#F44336",
    }

    sns.countplot(
        data=df,
        x="Classificacao_Risco",
        palette=colors,
        ax=ax,
        order=[
            "Baixo Risco (Bom Pagador)",
            "Médio Risco (Atenção)",
            "Alto Risco (Inadimplente)",
        ],
    )

    ax.set_title("Quantidade de Clientes por Faixa de Risco")
    ax.set_xlabel("Classificação")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=15)

    st.pyplot(fig)