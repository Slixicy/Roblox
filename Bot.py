import time
import requests

USER_ID = 318391715
WEBHOOK_URL = "https://discord.com/api/webhooks/1409979567078113420/0C5PGsAP0cDKY23Dnr4DhzqSFS0LTCUxp_ZaBsZ1AUC8hhW_9cTTU8378kf5CPJH_ieL"
ROBLOSECURITY = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhAB.1BDD39C289A1F818E72A0797AB4A379F5D732B681C7FD2D8B30DC542EAE206F408051CF8A49C3D999B47234AD65E767E88860724AAE0BF2A597536BF63AB0ADC73D36B6C375CFE80482046D1AC3DAAF97E32C295E7FC0F1201452AB00D574151929EFDB94AA680BD1E659F1A8899BAB58DC66EDDFAC2A73F068A1ED24F9244324AC3D033E188036CB7B78AAE9D0EE8BD749883BEF6C9516450D721A76901089AF87BCE9E92BA5CE735CF969AF78F5DAF77E4447DBE61BF2E62172C037E13158A737AD75E56D509427DF9354202EBCA245BAD796E6AB37DC86F16971384A4968D2EFF2BD94FD4DB56A496606FED0D56883EF178D773A3DE05E3C21EAFECC5E4CC674B4E1E225A33536391C08322861518AAD8F701253A42052C64B3471CDC81799A5BF1FA1EF30C229C61F82A8F7D96FC8E7E835DE3DF57E99AA8AEB57AA9B076205FA9BCF5D38557D42D90C790B251298DABF96D0FC3A39B0DE510084FDFCC4F552D880C2D1AA2CB90A64B47A2A2A115AD08C140FC7079AB41340A0B31DEECE72A2FCDDDA701FBAA82AE920F963C64CE8CD61C686E2F7CF31D35BCA181E229F1429DA39BDB2EA219AF65E29D12454384ADEDF3D76CF9B1535527E25E539FAD1BB1F12F5943391CCC4762F553B2537CA1C12ADB0DD39D742E49960F1E4556CD6EFFD55F72983D7BA6F9B78D20DD900D5096725EFEB79BE8739780C997EA80CDA6385CABF04BBD3E09237FB54097E85B253DC15F9189D9684333D8AAAEDEBC220CE338C655EBD5ADD6EFE6F865D600FBE759B26F0821E18DBDB82C378396106E28566F5D9F6715D4045F909F80D0096664ED7D81B5A107D0EF60E0820A46ACD6F00573362FAABC63FD0887E97FD4217B647FDE8CA2B6770D6401C5198A9439986F488F992B40F28E63EAA42741CC4B697D2FD1EBFD391ABE21C64776DBC7D3329282291690E67EDCA9ED5224188EAADE406A014034B7016D3F435F13AD8EC9D28EE10101C6611956FF0C3176A2CB6E7F8A762C69B3A5CE1E46A185927066A28A4EE880372C78C7B9942E7C3C8E872B59FE4142C5312D1291B888EF92BB5EB0767419D8997AF9A2A6C4315611F0C8707D5B057F6A924D4CC5A6777A3286E37806FFDB76945BB4CDF63964829D5B5C56924494B639AD0AD89D341BEBFB747050E8282A669F1D5EA9380C0A5EC18175C17791FA29E0FABB02B9E9EB563604A4045E7736BF7542BF25CD6919E8EFAB917C42B2FB6EEA5CCD4ED17CA35C78D85D715546729F2E5C"

HEADERS = {"Cookie": f".ROBLOSECURITY={ROBLOSECURITY}"}


class RobloxPresenceMonitor:
    def __init__(self, user_id: int, webhook_url: str):
        self.user_id = user_id
        self.webhook_url = webhook_url
        self.previous_status = None
        self.previous_game = None

    def fetch_presence(self) -> dict:
        response = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            headers=HEADERS,
            json={"userIds": [self.user_id]}
        )

        response.raise_for_status()
        return response.json()["userPresences"][0]

    def build_payload(self, game_name: str, place_id: int, game_id: str) -> dict:
        join_url = f"roblox://placeID={place_id}&gameID={game_id}" if place_id and game_id else None

        description_lines = [
            "🟢 Playing!",
            f"[Join Game!]({join_url})" if join_url else "Unavailable",
            f"**{game_name}**"
        ]

        description = "\n\n".join(description_lines)

        embed = {
            "title": "User Status",
            "description": description,
            "color": 0x00FF00
        }

        return {"content": None, "embeds": [embed]}

    def send_update(self, payload: dict):
        requests.post(self.webhook_url, json=payload).raise_for_status()

    def monitor(self, interval: int = 1):
        while True:
            try:
                presence = self.fetch_presence()
                status = presence.get("userPresenceType")

                if status == 2:
                    game_name = presence.get("lastLocation") or "Unknown Game"
                    place_id = presence.get("placeId")
                    game_id = presence.get("gameId")

                    if status != self.previous_status or game_name != self.previous_game:
                        payload = self.build_payload(game_name, place_id, game_id)
                        self.send_update(payload)
                        self.previous_status = status
                        self.previous_game = game_name
                else:
                    self.previous_status, self.previous_game = status, None

            except Exception as error:
                print(f"[Error] {error}")

            time.sleep(interval)

if __name__ == "__main__":
    monitor = RobloxPresenceMonitor(USER_ID, WEBHOOK_URL)
    monitor.monitor(interval=1)
