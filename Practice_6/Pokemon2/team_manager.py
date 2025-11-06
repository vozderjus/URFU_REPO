from pokemon import Pokemon

class TeamManager:
    """Класс для управления командой покемонов"""
    
    def __init__(self):
        self.team = []
        self.max_team_size = 6
    
    def add_pokemon(self, name):
        """Добавляет покемона в команду"""
        if len(self.team) >= self.max_team_size:
            print("Команда уже полна! Максимум 6 покемонов.")
            return False
        
        # Проверяем, есть ли уже такой покемон в команде
        if any(pokemon.name == name.lower() for pokemon in self.team):
            print(f"Покемон {name} уже есть в команде!")
            return False
        
        try:
            pokemon = Pokemon(name)
            self.team.append(pokemon)
            print(f"Покемон {name} успешно добавлен в команду!")
            return True
        except ValueError as e:
            print(e)
            return False
    
    def remove_pokemon(self, name):
        """Удаляет покемона из команды"""
        name = name.lower()
        for i, pokemon in enumerate(self.team):
            if pokemon.name == name:
                removed_pokemon = self.team.pop(i)
                print(f"Покемон {name} удален из команды.")
                return True
        
        print(f"Покемон {name} не найден в команде.")
        return False
    
    def view_team(self):
        """Показывает всех покемонов в команде"""
        if not self.team:
            print("Ваша команда пуста!")
            return
        
        print(f"\n=== ВАША КОМАНДА ({len(self.team)}/6) ===")
        for i, pokemon in enumerate(self.team, 1):
            print(f"{i}. {pokemon}")
    
    def find_pokemon(self, name):
        """Находит покемона по имени в команде"""
        name = name.lower()
        for pokemon in self.team:
            if pokemon.name == name:
                pokemon.display_info()
                return pokemon
        
        print(f"Покемон {name} не найден в команде.")
        return None
    
    def view_detailed_info(self):
        """Показывает подробную информацию обо всех покемонах в команде"""
        if not self.team:
            print("Ваша команда пуста!")
            return
        
        for pokemon in self.team:
            pokemon.display_info()
    
    def training_battle(self, pokemon1_name, pokemon2_name):
        """Проводит тренировочный бой между двумя покемонами"""
        pokemon1 = self.find_pokemon(pokemon1_name)
        pokemon2 = self.find_pokemon(pokemon2_name)
        
        if not pokemon1 or not pokemon2:
            print("Оба покемона должны быть в команде для боя!")
            return
        
        if pokemon1 == pokemon2:
            print("Нельзя устраивать бой между одним и тем же покемоном!")
            return
        
        print(f"\n=== ТРЕНИРОВОЧНЫЙ БОЙ ===")
        print(f"{pokemon1.name.upper()} vs {pokemon2.name.upper()}")
        print("=" * 30)
        
        # Рассчитываем силы
        attack1 = pokemon1.get_attack_power()
        defense1 = pokemon1.get_defense_power()
        attack2 = pokemon2.get_attack_power()
        defense2 = pokemon2.get_defense_power()
        
        # Сила покемона - среднее арифметическое атаки и защиты
        power1 = (attack1 + defense1) / 2
        power2 = (attack2 + defense2) / 2
        
        print(f"Сила {pokemon1.name}: {power1:.1f}")
        print(f"Сила {pokemon2.name}: {power2:.1f}")
        
        # Определяем победителя
        if power1 > power2:
            winner = pokemon1
            loser = pokemon2
        elif power2 > power1:
            winner = pokemon2
            loser = pokemon1
        else:
            print("Бой закончился ничьей!")
            return
        
        print(f"\n🏆 ПОБЕДИТЕЛЬ: {winner.name.upper()}!")
        print(f"💥 {winner.name} побеждает {loser.name} с преимуществом {abs(power1 - power2):.1f} очков силы!")