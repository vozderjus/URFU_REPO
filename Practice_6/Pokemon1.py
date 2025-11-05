import requests

class PokemonAPI:
    """Класс для взаимодействия с PokéAPI"""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_pokemon_list(self, limit=20):
        """Получает список покемонов"""
        url = f"{self.BASE_URL}/pokemon?limit={limit}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return [pokemon['name'] for pokemon in data['results']]
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении списка покемонов: {e}")
            return []
    
    def get_pokemon_details(self, pokemon_name):
        """Получает детальную информацию о покемоне"""
        url = f"{self.BASE_URL}/pokemon/{pokemon_name.lower()}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise PokemonNotFoundError(f"Покемон '{pokemon_name}' не найден!")
            else:
                raise requests.exceptions.RequestException(f"Ошибка HTTP: {e}")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Ошибка при получении информации: {e}")

class Pokemon:
    """Класс для представления покемона"""
    
    def __init__(self, data):
        self.data = data
        self.name = data['name'].capitalize()
        self.types = [type_info['type']['name'] for type_info in data['types']]
        self.weight = data['weight'] / 10  # Конвертируем в кг
        self.height = data['height'] / 10  # Конвертируем в метры
        self.abilities = [ability_info['ability']['name'] for ability_info in data['abilities']]
    
    def display_info(self):
        """Выводит информацию о покемоне"""
        print(f"\n=== Информация о покемоне ===")
        print(f"Имя: {self.name}")
        print(f"Тип: {', '.join(self.types)}")
        print(f"Вес: {self.weight} кг")
        print(f"Рост: {self.height} м")
        print(f"Способности: {', '.join(self.abilities)}")

class PokemonNotFoundError(Exception):
    """Кастомное исключение для случая, когда покемон не найден"""
    pass

class PokemonApp:
    """Основной класс приложения"""
    
    def __init__(self):
        self.api = PokemonAPI()
    
    def display_pokemon_list(self):
        """Отображает список покемонов"""
        print("Получаем список первых 20 покемонов...")
        pokemon_list = self.api.get_pokemon_list()
        
        if not pokemon_list:
            print("Не удалось получить список покемонов. Проверьте подключение к интернету.")
            return False
        
        print("\nСписок первых 20 покемонов:")
        for i, pokemon in enumerate(pokemon_list, 1):
            print(f"{i}. {pokemon.capitalize()}")
        
        return True
    
    def get_user_input(self):
        """Получает и валидирует ввод от пользователя"""
        while True:
            pokemon_name = input("\nВведите название покемона (или 'exit' для выхода): ").strip()
            
            if pokemon_name.lower() == 'exit':
                return None
            
            if not pokemon_name:
                print("Пожалуйста, введите название покемона.")
                continue
            
            if not self._validate_pokemon_name(pokemon_name):
                print("Некорректное название покемона. Используйте только буквы и цифры.")
                continue
            
            return pokemon_name
    
    def _validate_pokemon_name(self, name):
        """Проверяет корректность имени покемона"""
        return name.replace('-', '').isalnum()
    
    def search_pokemon(self, pokemon_name):
        """Поиск информации о покемоне"""
        try:
            pokemon_data = self.api.get_pokemon_details(pokemon_name)
            pokemon = Pokemon(pokemon_data)
            pokemon.display_info()
            return True
            
        except PokemonNotFoundError as e:
            print(f"Ошибка: {e}")
            print("Пожалуйста, проверьте правильность написания имени.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка: {e}")
            return False
    
    def ask_to_continue(self):
        """Спрашивает, хочет ли пользователь продолжить"""
        while True:
            choice = input("\nХотите найти другого покемона? (y/n): ").strip().lower()
            if choice in ['y', 'yes', 'да', 'д']:
                return True
            elif choice in ['n', 'no', 'нет', 'н']:
                return False
            else:
                print("Пожалуйста, введите 'y' для продолжения или 'n' для выхода.")
    
    def run(self):
        """Основной метод запуска приложения"""
        print("=== Программа для получения информации о покемонах ===\n")
        
        # Показываем список покемонов
        if not self.display_pokemon_list():
            return
        
        # Основной цикл программы
        while True:
            print("\n" + "="*50)
            
            # Получаем ввод от пользователя
            pokemon_name = self.get_user_input()
            
            if pokemon_name is None:
                print("Выход из программы...")
                break
            
            # Ищем информацию о покемоне
            self.search_pokemon(pokemon_name)
            
            # Предлагаем продолжить или выйти
            if not self.ask_to_continue():
                print("Выход из программы...")
                break

def main():
    """Точка входа в программу"""
    app = PokemonApp()
    app.run()

if __name__ == "__main__":
    main()