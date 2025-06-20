import os
import requests

# Create folders
os.makedirs("hero_icons", exist_ok=True)
os.makedirs("hero_full", exist_ok=True)

# OpenDota API and CDN base
API_URL = "https://api.opendota.com/api/heroStats"
CDN_BASE = "https://cdn.cloudflare.steamstatic.com"

# Download hero data
response = requests.get(API_URL)
heroes = response.json()

for hero in heroes:
    name = hero["localized_name"].replace(" ", "_").lower()
    icon_url = CDN_BASE + hero["icon"]
    full_url = CDN_BASE + hero["img"]

    icon_path = os.path.join("hero_icons", f"{name}.png")
    full_path = os.path.join("hero_full", f"{name}.png")

    try:
        with open(icon_path, "wb") as f:
            f.write(requests.get(icon_url).content)
        with open(full_path, "wb") as f:
            f.write(requests.get(full_url).content)
        print(f"Downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
