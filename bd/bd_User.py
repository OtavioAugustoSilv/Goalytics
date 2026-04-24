from bd.db_connection import conectar
import sqlite3

# 🔹 Criar tabela (executa 1x quando rodar o arquivo)
def criar_tabela_users():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        time_favorito_id INTEGER,
        FOREIGN KEY (time_favorito_id) REFERENCES times(id)
    )
    """)

    conn.commit()
    conn.close()


# 🔹 Criar usuário
def criar_usuario(nome, email, senha, time_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (nome, email, senha, time_favorito_id)
            VALUES (?, ?, ?, ?)
        """, (nome, email, senha, time_id))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# 🔹 Buscar usuário (login)
def buscar_usuario(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ? AND senha = ?
    """, (email, senha))

    user = cursor.fetchone()
    conn.close()

    return user