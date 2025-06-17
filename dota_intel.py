from heroes import fetch_hero_stats
from setup import setup_heroes_database
def main_menu():
    while True:
        print("\n=== Dota Intelligence CLI ===")
        print("1. Setup Database (Obtener todos los héroes)")
        print("2. Fetch Hero (Obtener detalles de un héroe)")
        print("0. Salir")

        option = input("Selecciona una opción: ").strip()
        if option == "1":
            setup_heroes_database()
        elif option == "2":
            fetch_hero_stats()
        elif option == "0":
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main_menu()
