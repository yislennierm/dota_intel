import requests
from db import get_driver

def setup_heroes_database():
    print("🔄 Fetching all heroes from OpenDota...")
    try:
        res = requests.get("https://api.opendota.com/api/heroStats")
        heroes = res.json()
        with get_driver().session() as session:
            for hero in heroes:
                session.run(
                    "MERGE (h:Hero {id: $id}) "
                    "SET h.name = $name, h.localized_name = $localized_name, h.base_health = $health",
                    {
                        "id": hero["id"],
                        "name": hero["name"],
                        "localized_name": hero["localized_name"],
                        "health": hero["base_health"]
                    }
                )
        print(f"✅ Stored {len(heroes)} heroes in the database.")
    except Exception as e:
        print("❌ Error setting up heroes database:", e)
