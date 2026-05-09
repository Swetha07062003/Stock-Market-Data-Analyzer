import sqlite3

conn = sqlite3.connect("db/market.db")

cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

print("\nDATABASE TABLES:\n")

for table in tables:
    print(table[0])

conn.close()