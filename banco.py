import sqlite3


def inicializar_banco():
  conn = sqlite3.connect('risco_credito.db')
  cursor = conn.cursor()

  # 1. Tabela de Clientes
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        renda_mensal REAL,
        score_serasa INTEGER
    )
    ''')

  # 2. Tabela de Empréstimos
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS emprestimos (
        emprestimo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        valor_contratado REAL,
        qtd_parcelas INTEGER,
        data_contratacao DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    ''')

  # 3. Tabela de Pagamentos
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS pagamentos (
        pagamento_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emprestimo_id INTEGER,
        numero_parcela INTEGER,
        status TEXT, -- 'PAGO' ou 'ATRASADO'
        FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(emprestimo_id)
    )
    ''')

  # Insere dados de teste se o banco estiver vazio
  cursor.execute('SELECT COUNT(*) FROM clientes')
  if cursor.fetchone()[0] == 0:
    cursor.executemany(
        '''
        INSERT INTO clientes (nome, idade, renda_mensal, score_serasa) 
        VALUES (?, ?, ?, ?)
        ''',
        [
            ('Lucas Mendes', 34, 4500.0, 720),
            ('Mariana Santos', 28, 2800.0, 480),
            ('Carlos Andrade', 45, 8200.0, 310),
            ('Fernanda Lima', 22, 3100.0, 650),
        ],
    )

    cursor.executemany(
        '''
        INSERT INTO emprestimos (cliente_id, valor_contratado, qtd_parcelas, data_contratacao)
        VALUES (?, ?, ?, DATE('now'))
        ''',
        [(1, 10000.0, 12), (2, 5000.0, 12), (3, 20000.0, 24), (4, 4000.0, 6)],
    )

    cursor.executemany(
        '''
        INSERT INTO pagamentos (emprestimo_id, numero_parcela, status)
        VALUES (?, ?, ?)
        ''',
        [
            (1, 1, 'PAGO'),
            (1, 2, 'PAGO'),
            (2, 1, 'PAGO'),
            (2, 2, 'ATRASADO'),
            (3, 1, 'ATRASADO'),
            (3, 2, 'ATRASADO'),
            (4, 1, 'PAGO'),
            (4, 2, 'PAGO'),
        ],
    )

  conn.commit()
  conn.close()
  print('✅ Banco de dados inicializado com sucesso!')


if __name__ == '__main__':
  inicializar_banco()