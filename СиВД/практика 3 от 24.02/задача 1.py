import pandas as pd


df = pd.read_csv('СиВД/практика 3 от 24.02/vgsales.csv')

# 1
df['Year'] = pd.to_numeric(df['Year'])

# 2
df = df.dropna(subset=['Year'])

# первое и второе лучше поменять местами, чтобы не возникло ошибок

# 3
sales_columns = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']
for col in sales_columns:
    print(f"Тип столбца: {df[col].dtype}")

# 4
df['Total_Regional_Sales'] = df['NA_Sales'] + df['EU_Sales'] \
    + df['JP_Sales'] + df['Other_Sales']

# 5
df['Sales_Diff'] = df['Global_Sales'] - df['Total_Regional_Sales']

# 6
final_col = ['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales', 'Total_Regional_Sales', 'Sales_Diff']

final_df = df[final_col]

filter_con = final_df['Sales_Diff'] != 0
df_filtered = final_df[filter_con]

sorted_df = df_filtered.sort_values(by='Sales_Diff', ascending=False)

sorted_df.to_csv('vgsales_cleaned_analysis.csv', index=False)

print(df.head())
print(sorted_df['Sales_Diff'].describe())
