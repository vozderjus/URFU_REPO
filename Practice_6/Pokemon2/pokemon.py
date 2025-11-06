import requests

class Pokemon:
    """Класс для представления покемона"""
    
    def __init__(self, name):
        self.name = name.lower()
        self.data = self._fetch_data()
        if self.data:
            self._initialize_from_data()
        else:
            raise ValueError(f"Покемон '{name}' не найден!")
    
    def _fetch_data(self):
        """Получает данные покемона из API"""
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{self.name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def _initialize_from_data(self):
        """Инициализирует атрибуты из полученных данных"""
        self.id = self.data['id']
        self.types = [t['type']['name'] for t in self.data['types']]
        self.abilities = [a['ability']['name'] for a in self.data['abilities']]
        self.stats = {stat['stat']['name']: stat['base_stat'] for stat in self.data['stats']}
        self.height = self.data['height']
        self.weight = self.data['weight']
        self.moves = [move['move']['name'] for move in self.data['moves'][:5]]  # Первые 5 способностей
    
    def get_attack_power(self):
        """Рассчитывает силу атаки на основе статистики"""
        return (self.stats['attack'] + self.stats['special-attack']) / 2
    
    def get_defense_power(self):
        """Рассчитывает силу защиты на основе статистики"""
        return (self.stats['defense'] + self.stats['special-defense']) / 2
    
    def display_info(self):
        """Выводит подробную информацию о покемоне"""
        print(f"\n=== {self.name.upper()} ===")
        print(f"ID: {self.id}")
        print(f"Типы: {', '.join(self.types)}")
        print(f"Способности: {', '.join(self.abilities[:3])}")  # Первые 3 способности
        print(f"Рост: {self.height / 10} м")
        print(f"Вес: {self.weight / 10} кг")
        print("\nСтатистика:")
        for stat, value in self.stats.items():
            print(f"  {stat}: {value}")
        print(f"\nИзвестные движения: {', '.join(self.moves)}")
    
    def __str__(self):
        return f"{self.name.title()} (ID: {self.id}, Типы: {', '.join(self.types)})"
    
    def __eq__(self, other):
        if isinstance(other, Pokemon):
            return self.name == other.name
        return False