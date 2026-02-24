import sqlite3
import pandas as pd

conn = sqlite3.connect("/Users/vozderjus/Documents/VS_Code/URFU_REPO/СиВД/практика 3 от 24.02/database.sqlite")

df = pd.read_sql("SELECT airline from Tweets;", conn)

conn.close()

print(df.head())

df = df.drop_duplicates().sort_values("airline")

out = sqlite3.connect("airline.sqlite")
df.to_sql("airline", out, index=False)
out.close()