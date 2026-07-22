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

# Criar a tabela no banco de dados se não existir
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

# Função para calcular a classe de risco com base no Score e Renda
def calcular_risco(score, renda, valor_parcela):
    comprometimento_renda = (valor_parcela / renda) * 100
    
    if score >= 700 and comprometimento_renda <= 30:
        return "Baixo Risco"
    elif score >= 500 and comprometimento_renda <= 50:
        return "Médio Risco"
    else:
        return "Alto Risco"

# Inicializar o banco ao carregar o app
inicializar_banco()

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.header("📋 Cadastro & Simulação")

nome = st.sidebar.text_input("Nome do Cliente")
idade = st.sidebar.number_input("Idade", min_value=18, max_value=100, value=25)
renda = st.sidebar.number_input("Renda Mensal (R$)", min_value=0.0, value=3000.0, step=500.0)
score = st.sidebar.slider("Score do Serasa/SPC", min_value=0, max_value=1000, value=650)

st.sidebar.subheader("Dados do Empréstimo")
valor_emprestimo = st.sidebar.number_input("Valor Solicitado (R$)", min_value=0.0, value=10000.0, step=1000.0)
num_parcelas = st.sidebar.slider("Quantidade de Parcelas", min_value=1, max_value=72, value=12)

# Cálculo automático da parcela (com taxa simples de juros simulada de 2% a.m.)
taxa_juros = 0.02
total_com_juros = valor_emprestimo * (1 + (taxa_juros * num_parcelas))
valor_parcela = total_com_juros / num_parcelas if num_parcelas > 0 else 0

st.sidebar.info(f"**Valor estimado da parcela:** R$ {valor_parcela:.2f}")

# Botão de Cadastrar Cliente
if st.sidebar.button("💾 Cadastrar e Analisar Risco"):
    if nome.strip() == "":
        st.sidebar.error("Por favor, preencha o nome do cliente.")
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
        
        st.sidebar.success(f"Cliente {nome} cadastrado! Classificação: **{risco}**")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Gerenciamento do Banco")

# 🔴 BOTÃO PARA APAGAR A TABELA / ZERAR DADOS
confirmar_limpeza = st.sidebar.checkbox("Confirmar exclusão de TODOS os registros")

if st.sidebar.button("🗑️ Apagar Todos os Dados"):
    if confirmar_limpeza:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes")
        conn.commit()
        conn.close()
        st.sidebar.success("Todos os registros foram apagados com sucesso!")
        st.rerun()
    else:
        st.sidebar.warning("Marque a caixa de confirmação acima para poder apagar.")


# --- PAINEL PRINCIPAL ---
st.title("💳 Sistema de Análise de Risco de Crédito")
st.markdown("Acompanhe os clientes cadastrados e a distribuição da carteira de risco.")

# Carregar dados do banco para o Pandas
conn = conectar_banco()
df = pd.read_sql_query("SELECT * FROM clientes", conn)
conn.close()

if not df.empty:
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Clientes", len(df))
    col2.metric("Total Solicitado", f"R$ {df['valor_emprestimo'].sum():,.2f}")
    col3.metric("Média de Renda", f"R$ {df['renda'].mean():,.2f}")
    col4.metric("Média de Score", f"{int(df['score'].mean())}")

    st.markdown("---")

    # Layout de 2 colunas para Tabela e Gráfico
    col_tabela, col_grafico = st.columns([1.2, 0.8])

    with col_tabela:
        st.subheader("📋 Tabela de Clientes Cadastrados")
        st.dataframe(
            df[['id', 'nome', 'renda', 'score', 'valor_emprestimo', 'valor_parcela', 'classificacao_risco']],
            use_container_width=True
        )

    with col_grafico:
        st.subheader("📊 Distribuição por Faixa de Risco")
        fig, ax = plt.subplots(figsize=(5, 4))
        
        cores = {"Baixo Risco": "#2ecc71", "Médio Risco": "#f1c40f", "Alto Risco": "#e74c3c"}
        
        contagem_risco = df['classificacao_risco'].value_counts().reset_index()
        contagem_risco.columns = ['Risco', 'Quantidade']
        
        sns.barplot(
            data=contagem_risco, 
            x='Risco', 
            y='Quantidade', 
            palette=cores, 
            ax=ax
        )
        
        ax.set_ylabel("Quantidade de Clientes")
        ax.set_xlabel("")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("Nenhum cliente cadastrado no banco de dados no momento. Utilize a barra lateral ao lado para cadastrar o primeiro!")
