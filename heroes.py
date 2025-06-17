import requests
from db import driver  # ✅ Import shared Neo4j connection

def fetch_hero_stats():
    url = "https://api.opendota.com/api/heroStats"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ No se pudo obtener la información de los héroes.")
        return

    heroes = response.json()
    print(f"🔄 Procesando {len(heroes)} héroes...")

    with driver.session() as session:
        for hero in heroes:
            session.run(
                """
                MERGE (h:Hero {id: $id})
                SET h.name = $name,
                    h.localized_name = $localized_name,
                    h.primary_attr = $primary_attr,
                    h.attack_type = $attack_type,
                    h.roles = $roles,
                    h.base_health = $base_health,
                    h.base_health_regen = $base_health_regen,
                    h.base_mana = $base_mana,
                    h.base_mana_regen = $base_mana_regen,
                    h.base_armor = $base_armor,
                    h.base_mr = $base_mr,
                    h.base_attack_min = $base_attack_min,
                    h.base_attack_max = $base_attack_max,
                    h.base_str = $base_str,
                    h.base_agi = $base_agi,
                    h.base_int = $base_int,
                    h.str_gain = $str_gain,
                    h.agi_gain = $agi_gain,
                    h.int_gain = $int_gain,
                    h.attack_range = $attack_range,
                    h.projectile_speed = $projectile_speed,
                    h.attack_rate = $attack_rate,
                    h.move_speed = $move_speed,
                    h.turn_rate = $turn_rate,
                    h.legs = $legs
                """,
                {
                    "id": hero["id"],
                    "name": hero["name"],
                    "localized_name": hero["localized_name"],
                    "primary_attr": hero["primary_attr"],
                    "attack_type": hero["attack_type"],
                    "roles": hero["roles"],
                    "base_health": hero["base_health"],
                    "base_health_regen": hero["base_health_regen"],
                    "base_mana": hero["base_mana"],
                    "base_mana_regen": hero["base_mana_regen"],
                    "base_armor": hero["base_armor"],
                    "base_mr": hero["base_mr"],
                    "base_attack_min": hero["base_attack_min"],
                    "base_attack_max": hero["base_attack_max"],
                    "base_str": hero["base_str"],
                    "base_agi": hero["base_agi"],
                    "base_int": hero["base_int"],
                    "str_gain": hero["str_gain"],
                    "agi_gain": hero["agi_gain"],
                    "int_gain": hero["int_gain"],
                    "attack_range": hero["attack_range"],
                    "projectile_speed": hero["projectile_speed"],
                    "attack_rate": hero["attack_rate"],
                    "move_speed": hero["move_speed"],
                    "turn_rate": hero.get("turn_rate", 0),
                    "legs": hero["legs"]
                }
            )

    print("✅ Base de datos de héroes actualizada con estadísticas completas.")
