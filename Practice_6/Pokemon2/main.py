from team_manager import TeamManager

def display_menu():
    """Отображает главное меню"""
    print("\n" + "=" * 50)
    print("          МЕНЕДЖЕР КОМАНДЫ POKÉMON")
    print("=" * 50)
    print("1. Добавить покемона в команду")
    print("2. Удалить покемона из команды")
    print("3. Просмотреть команду")
    print("4. Найти покемона по имени")
    print("5. Подробная информация о команде")
    print("6. Тренировочный бой")
    print("7. Выйти")
    print("=" * 50)

def main():
    manager = TeamManager()
    
    print("Добро пожаловать в менеджер команды Pokémon!")
    
    while True:
        display_menu()
        choice = input("\nВыберите действие (1-7): ").strip()
        
        if choice == '1':
            name = input("Введите имя покемона для добавления: ").strip()
            manager.add_pokemon(name)
        
        elif choice == '2':
            name = input("Введите имя покемона для удаления: ").strip()
            manager.remove_pokemon(name)
        
        elif choice == '3':
            manager.view_team()
        
        elif choice == '4':
            name = input("Введите имя покемона для поиска: ").strip()
            manager.find_pokemon(name)
        
        elif choice == '5':
            manager.view_detailed_info()
        
        elif choice == '6':
            if len(manager.team) < 2:
                print("Для боя нужно как минимум 2 покемона в команде!")
                continue
            
            manager.view_team()
            print("\nВыберите покемонов для боя:")
            pokemon1 = input("Имя первого покемона: ").strip()
            pokemon2 = input("Имя второго покемона: ").strip()
            manager.training_battle(pokemon1, pokemon2)
        
        elif choice == '7':
            print("Спасибо за использование менеджера команды Pokémon!")
            break
        
        else:
            print("Неверный выбор. Пожалуйста, выберите действие от 1 до 7.")

if __name__ == "__main__":
    main()