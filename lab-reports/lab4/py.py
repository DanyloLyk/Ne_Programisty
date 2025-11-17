import sqlite3

# Підключаємося до бази
conn = sqlite3.connect("instance/mydatabase.db")
cur = conn.cursor()

# Виводимо всі таблиці
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

for table_name, in tables:
    print(f"\nТаблиця: {table_name}")
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    for row in rows:
        print(row)

conn.close()
