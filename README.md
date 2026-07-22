# 💳 Sistema de Análise de Risco de Crédito

> Aplicação web interativa para simulação, análise de risco e gerenciamento de carteira de crédito em tempo real.

👉 **Acesse o aplicativo rodando ao vivo:** [https://app-web-analise-risco-credito-miguel.streamlit.app/]

---

## 📋 Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de simular o processo de tomada de decisão na concessão de crédito financeiro. O sistema calcula automaticamente o risco daoperação (classificado em **Baixo**, **Médio** ou **Alto Risco**) analisando variáveis como renda mensal, score de crédito e o comprometimento da renda em relação ao valor da parcela solicitada.

A aplicação conta com uma interface intuitiva e está integrada a um banco de dados relacional **SQLite**, permitindo a execução de operações **CRUD** completas diretamente pela web.

---

## ✨ Funcionalidades

- ➕ **Cadastro de Clientes (Create):** Inserção de novos perfis com cálculo automático de juros, parcelamento e classificação de risco.
- 📋 **Visualização de Carteira (Read):** Tabela em tempo real com métricas consolidadas (Total Solicitado, Média de Renda, Score Médio) e distribuição gráfica dos riscos.
- ✏️ **Atualização de Dados (Update):** Alteração de registros existentes (Score, Renda ou Valor Solicitado) via comandos SQL, recalculando a classe de risco de forma dinâmica.
- 🗑️ **Exclusão de Registros (Delete):** Remoção individual de clientes ou opção de reset completo do banco de dados via SQL (`DELETE`).

---

## 📊 Regra de Negócio

A classificação de risco do cliente segue a lógica abaixo:

- **🟢 Baixo Risco:** Score $\ge$ 700 e comprometimento da renda com a parcela $\le$ 30%.
- **🟡 Médio Risco:** Score $\ge$ 500 e comprometimento da renda com a parcela $\le$ 50%.
- **🔴 Alto Risco:** Score abaixo de 500 ou comprometimento de renda superior a 50%.

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/):** Linguagem principal do projeto.
- **[Streamlit](https://streamlit.io/):** Framework para construção da interface web interativa.
- **[SQLite3](https://www.sqlite.org/):** Banco de dados relacional para persistência dos dados.
- **[Pandas](https://pandas.pydata.org/):** Leitura de consultas SQL e manipulação de dataframes.
- **[Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/):** Geração do painel gráfico visual.

---

## 🚀 Como Executar o Projeto Localmente

Se desejar rodar o projeto no seu computador:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
   cd SEU_REPOSITORIO
