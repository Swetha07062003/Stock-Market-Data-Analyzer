import sqlite3
import pandas as pd

conn = sqlite3.connect("db/market.db")

query = """
SELECT *
FROM indicators_daily
LIMIT 10
"""

df = pd.read_sql(query, conn)

print("\nINDICATOR DATA:\n")

print(df)

conn.close()