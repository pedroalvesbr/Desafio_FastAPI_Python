import sqlite3

# conecta no banco
conn = sqlite3.connect("../app.db")
cursor = conn.cursor()

# lista todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabelas:", tables)

# cursor.execute("INSERT INTO voice_actors (name, country) VALUES (?, ?)", ("John Doe", "USA"))
# conn.commit()


# mostra os dados da tabela voice_actors
cursor.execute("SELECT * FROM voice_actors;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
