import requests
from db import driver  # ✅ Import shared Neo4j connection

def fetch_hero():
    hero_name = input("Escribe el nombre del héroe (ej: axe): ").strip().lower()

    # Step 1: Get all hero stats to find the correct hero ID
    stats_url = "https://api.opendota.com/api/heroStats"
    stats_response = requests.get(stats_url)
    if stats_response.status_code != 200:
        print("❌ No se pudo obtener la información de los héroes.")
        return

    heroes = stats_response.json()
    hero_data = None
    for hero in heroes:
        if hero_name == hero["localized_name"].lower() or hero_name == hero["name"].replace("npc_dota_hero_", ""):
            hero_data = hero
            break

    if not hero_data:
        print("❌ Héroe no encontrado. Verifica el nombre.")
        return

    hero_id = hero_data["id"]
    print(f"✅ Héroe encontrado: {hero_data['localized_name']} (ID: {hero_id})")

    # Step 2: Fetch matchups
    matchup_url = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
    matchup_response = requests.get(matchup_url)
    if matchup_response.status_code != 200:
        print("❌ No se pudo obtener los matchups.")
        return
    matchups = matchup_response.json()

    # Step 3: Update hero node and relationships in Neo4j
    with driver.session() as session:
        # Update hero stats
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
                "id": hero_id,
                "name": hero_data["name"],
                "localized_name": hero_data["localized_name"],
                "primary_attr": hero_data["primary_attr"],
                "attack_type": hero_data["attack_type"],
                "roles": hero_data["roles"],
                "base_health": hero_data["base_health"],
                "base_health_regen": hero_data["base_health_regen"],
                "base_mana": hero_data["base_mana"],
                "base_mana_regen": hero_data["base_mana_regen"],
                "base_armor": hero_data["base_armor"],
                "base_mr": hero_data["base_mr"],
                "base_attack_min": hero_data["base_attack_min"],
                "base_attack_max": hero_data["base_attack_max"],
                "base_str": hero_data["base_str"],
                "base_agi": hero_data["base_agi"],
                "base_int": hero_data["base_int"],
                "str_gain": hero_data["str_gain"],
                "agi_gain": hero_data["agi_gain"],
                "int_gain": hero_data["int_gain"],
                "attack_range": hero_data["attack_range"],
                "projectile_speed": hero_data["projectile_speed"],
                "attack_rate": hero_data["attack_rate"],
                "move_speed": hero_data["move_speed"],
                "turn_rate": hero_data.get("turn_rate", 0),
                "legs": hero_data["legs"]
            }
        )

        # Create matchup relationships
        for m in matchups:
            session.run(
                """
                MATCH (h1:Hero {id: $source_id}), (h2:Hero {id: $target_id})
                MERGE (h1)-[r:MATCHUP]->(h2)
                SET r.games_played = $games_played,
                    r.wins = $wins
                """,
                {
                    "source_id": hero_id,
                    "target_id": m["hero_id"],
                    "games_played": m["games_played"],
                    "wins": m["wins"]
                }
            )

    print("📥 Datos del héroe y sus matchups actualizados en Neo4j.")
