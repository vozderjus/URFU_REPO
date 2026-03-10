# import pandas as pd


# def Series():
#     nums = list(range(1, 27))

#     chars = [chr(i) for i in range(ord('a'), ord('z') + 1)]

#     series = pd.Series(data=nums, index=chars)

#     return series


# ---


# import pandas as pd


# def create_df(dictionary):
#     df = pd.DataFrame(dictionary)

#     return df.head(3)


# ---


# import pandas as pd


# csv_file = pd.read_csv('user_behavior_dataset.csv')

# df = pd.DataFrame(csv_file)

# df_filtered = df[df['Age'] == 19]

# df_filtered.to_csv('age_filtered.csv', index=False)


# ---


import sqlite3
import pandas as pd

conn = sqlite3.connect('european_database.sqlite')

query = """
SELECT
m.*, d.name, d.country
FROM matchs m
JOIN divisions d ON d.division == m.Div
"""
df = pd.read_sql_query(query, conn)

conn.close()

df_country = df[['country']].drop_duplicates()

new_conn = sqlite3.connect('new_database.sqlite')
df_country.to_sql('countries', new_conn, if_exists='replace', index=False)

new_conn.close()


# ---

# import pandas as pd

# df = pd.read_json('games_metadata.json', lines=True)

# if df['tags'].apply(type).eq(list).any():
#     df['tags'] = df['tags'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

# mask_strategy = df['tags'].astype(str).str.contains('Strategy', na=False)
# mask_rts = df['tags'].astype(str).str.contains('RTS', na=False)
# df_filtered = df[mask_strategy & mask_rts]


# pivot_table = df_filtered.groupby('genre').size().reset_index(name='count')
# table_sorted = pivot_table.sort_values('count', ascending=False)

# table_sorted.to_json('games_strategy_rts.json', index=False)


# ---

# import pandas as pd

# df = pd.read_excel('54-iip_24.xlsx', header=None)

# df = df.dropna(how='all')
