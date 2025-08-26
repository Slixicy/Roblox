import time
import requests

USERNAME = "Ev_stef"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1409979567078113420/0C5PGsAP0cDKY23Dnr4DhzqSFS0LTCUxp_ZaBsZ1AUC8hhW_9cTTU8378kf5CPJH_ieL"
POLL_INTERVAL = 1


def get_user_id(username):
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    resp = requests.get(url).json()
    return resp["Id"]


def fetch_presence(user_id):
    url = "https://presence.roblox.com/v1/presence/users"
    resp = requests.post(url, json={"userIds": [user_id]})
    resp.raise_for_status()
    return resp.json()["userPresences"][0]


def get_avatar_url(user_id):
    """Get Roblox avatar thumbnail URL."""
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    resp = requests.get(url).json()
    return resp["data"][0]["imageUrl"]


def send_webhook(game_name, place_id, game_id, avatar_url):
    join_url = f"roblox://placeId={place_id}&gameInstanceId={game_id}"
    payload = {
        "embeds": [
            {
                "title": f"{USERNAME} is currently playing: {game_name}",
                "url": join_url,
                "description": "Click the title to join their server!",
                "thumbnail": {"url": avatar_url},  # show their character
                "color": 3066993  # optional: green accent
            }
        ]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)


def main():
    user_id = get_user_id(USERNAME)
    last_game = None
    print(f"[INFO] Monitoring {USERNAME} (ID: {user_id})")

    while True:
        try:
            presence = fetch_presence(user_id)
            if presence["userPresenceType"] == 2:  # In game
                game_name = presence.get("lastLocation") or "Unknown"
                place_id = presence.get("placeId")
                game_id = presence.get("gameId")

                if game_id and game_id != last_game:
                    avatar_url = get_avatar_url(user_id)
                    send_webhook(game_name, place_id, game_id, avatar_url)
                    print(f"[INFO] Webhook sent: {game_name}")
                    last_game = game_id
            else:
                print("[INFO] Not in game.")
                last_game = None

        except Exception as e:
            print("[ERROR]", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
