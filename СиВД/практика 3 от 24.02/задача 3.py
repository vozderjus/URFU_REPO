import pandas as pd

df = pd.read_json("/Users/vozderjus/Documents/VS_Code/URFU_REPO/СиВД/практика 3 от 24.02/steam_games.json")


# Функция для проверки наличия жанра Action
def has_action(genre):
    if isinstance(genre, list):
        return 'Action' in genre
    elif isinstance(genre, str):
        return 'Action' in genre
    return False


# Функция для проверки Positive оценки
def is_positive(rating):
    if isinstance(rating, str):
        return 'positive' in rating.lower()
    return False


# Функция для извлечения минимального числа владельцев
def get_owners_count(owners):
    if isinstance(owners, str) and '-' in owners:
        return int(owners.split('-')[0])
    return 0


# Применяем фильтры
df_filtered = df[
    df['genre'].apply(has_action) &
    df['rating'].apply(is_positive) &
    df['owners'].apply(get_owners_count) > 10000
].copy()

# Создаем сводную таблицу по платформам
platform_pivot = df_filtered.explode('platforms').groupby('platforms').size().reset_index()
platform_pivot.columns = ['platform', 'games_count']
platform_pivot = platform_pivot.sort_values('games_count', ascending=False)

# Сохраняем результат
platform_pivot.to_json('steam_games_analyze.json', orient='records', indent=2)

print(f"Найдено игр: {len(df_filtered)}")
print(platform_pivot.head(10))
