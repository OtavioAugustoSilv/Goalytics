import sqlite3
import pandas as pd
conn = sqlite3.connect("../futebol.db")
cursor = conn.cursor()

# 1. Criar nova tabela temporária
cursor.execute("""
CREATE TABLE times_novo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    liga TEXT
)
""")

# 2. Copiar dados (SEM id antigo)
cursor.execute("""
INSERT INTO times_novo (nome, liga)
SELECT nome, liga FROM times
""")

# 3. Deletar tabela antiga
cursor.execute("DROP TABLE times")

# 4. Renomear nova tabela
cursor.execute("ALTER TABLE times_novo RENAME TO times")

conn.commit()


# 🔹 Conexão
def conectar():
    return sqlite3.connect("../futebol.db")

# 🔹 Arquivos locais
arquivos = {
    "E0": "ligaInglaterra.csv",
    "D1": "ligaAlemanha.csv",
    "SP1": "ligaEspanha.csv"
}

# 🔹 Inserir times
def inserir_times():
    conn = conectar()
    cursor = conn.cursor()

    for liga, arquivo in arquivos.items():
        df = pd.read_csv(arquivo)

        times = set()

        for _, row in df.iterrows():
            times.add(row["HomeTeam"])
            times.add(row["AwayTeam"])

        for time in times:
            try:
                cursor.execute("""
                    INSERT INTO times (nome, liga)
                    VALUES (?, ?)
                """, (time, liga))
            except:
                # ignora duplicado
                pass

    conn.commit()
    conn.close()

    print("✅ Times inseridos com sucesso!")

# 🔹 Rodar
conn.close()
inserir_times()
print("Tabela recriada com IDs corrigidos!")