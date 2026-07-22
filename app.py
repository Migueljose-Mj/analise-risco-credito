import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def conectar():
  return sqlite3.connect('risco_credito.db')


def cadastrar_cliente():
  print('\n--- 📥 CADASTRO DE CLIENTE E EMPRÉSTIMO ---')
  nome = input('Nome completo: ')
  idade = int(input('Idade: '))
  renda = float(input('Renda Mensal (R$): '))
  score = int(input('Score Serasa (0-1000): '))
  valor = float(input('Valor do Empréstimo (R$): '))
  parcelas = int(input('Quantidade de Parcelas: '))

  conn = conectar()
  cursor = conn.cursor()

  cursor.execute(
      '''
        INSERT INTO clientes (nome, idade, renda_mensal, score_serasa)
        VALUES (?, ?, ?, ?)
    ''',
      (nome, idade, renda, score),
  )

  cliente_id = cursor.lastrowid

  cursor.execute(
      '''
        INSERT INTO emprestimos (cliente_id, valor_contratado, qtd_parcelas, data_contratacao)
        VALUES (?, ?, ?, DATE('now'))
    ''',
      (cliente_id, valor, parcelas),
  )

  conn.commit()
  conn.close()
  print(f"\n✅ Cliente '{nome}' cadastrado com sucesso!")


def relatorio_risco():
  conn = conectar()
  query = """
    SELECT 
        c.cliente_id AS ID,
        c.nome AS Cliente,
        c.renda_mensal AS Renda,
        c.score_serasa AS Score,
        e.valor_contratado AS Valor,
        SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) AS Atrasos,
        
        CASE 
            WHEN SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) >= 2 OR c.score_serasa < 400 
                THEN 'Alto Risco (Inadimplente)'
            WHEN SUM(CASE WHEN p.status = 'ATRASADO' THEN 1 ELSE 0 END) = 1 OR c.score_serasa BETWEEN 400 AND 600 
                THEN 'Médio Risco (Atenção)'
            ELSE 'Baixo Risco (Bom Pagador)'
        END AS Risco

    FROM clientes c
    JOIN emprestimos e ON c.cliente_id = e.cliente_id
    LEFT JOIN pagamentos p ON e.emprestimo_id = p.emprestimo_id
    GROUP BY c.cliente_id, e.emprestimo_id;
    """
  df = pd.read_sql_query(query, conn)
  conn.close()

  print('\n📊 RELATÓRIO DE RISCO DE CRÉDITO (SQL):')
  print(df.to_string(index=False))
  return df


def gerar_grafico():
  df = relatorio_risco()
  plt.figure(figsize=(8, 5))
  sns.countplot(
      data=df, x='Risco', palette=['#4CAF50', '#FFC107', '#F44336']
  )
  plt.title('Distribuição do Risco da Carteira')
  plt.xlabel('Categoria de Risco')
  plt.ylabel('Qtd de Clientes')
  plt.tight_layout()
  plt.show()


def menu():
  while True:
    print('\n' + '=' * 35)
    print('  SISTEMA DE ANÁLISE DE CRÉDITO')
    print('=' * 35)
    print('1. Cadastrar Novo Cliente')
    print('2. Ver Relatório de Risco (SQL)')
    print('3. Gerar Gráfico no Matplotlib')
    print('4. Sair')

    opcao = input('\nEscolha uma opção (1-4): ')

    if opcao == '1':
      cadastrar_cliente()
    elif opcao == '2':
      relatorio_risco()
    elif opcao == '3':
      gerar_grafico()
    elif opcao == '4':
      print('\nSaindo... Bom trabalho!')
      break
    else:
      print('\nOpção inválida!')


if __name__ == '__main__':
  # Garante que o banco existe antes de abrir o menu
  from banco import inicializar_banco

  inicializar_banco()
  menu()
  