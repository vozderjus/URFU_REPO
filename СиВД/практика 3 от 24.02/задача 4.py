import pandas as pd

df = pd.read_parquet("/Users/vozderjus/Documents/VS_Code/URFU_REPO/СиВД/практика 3 от 24.02/UNSW_NB15_testing-set.parquet")

df_generic = df[df['attack_cat'].str.contains("Generic")].copy()

print(df.head())

pivot = df_generic.groupby('proto').size().reset_index(name='count')
pivot = pivot.sort_values('count', ascending=False)

pivot.to_parquet('UNSW_NB15_analyze.parquet', index=False)
print("\nРезультат сохранен в UNSW_NB15_analyze.parquet")