import requests

STEAM_API_KEY = "198756A2555931C7AEA2AD3899502B1A"
STEAM_ID64 = "88850768"  # Replace with your actual SteamID64

def check_steam_game_status(steam_id64):
    url = (
        f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        f"?key={STEAM_API_KEY}&steamids={steam_id64}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        print("❌ API request failed.")
        return

    data = response.json()
    players = data.get("response", {}).get("players", [])
    if not players:
        print("❌ Player not found.")
        return

    player = players[0]
    if "gameid" in player:
        print(f"🎮 Player is currently in-game: {player['gameextrainfo']} (Game ID: {player['gameid']})")
    else:
        print("❌ Player is not currently in a game.")

if __name__ == "__main__":
    check_steam_game_status(STEAM_ID64)
