import os
import sys

import discord
import dotenv
import requests
import tweepy

dotenv.load_dotenv()


class Chatwork:
    def __init__(self, room_name: str, message: str) -> None:
        self.api_url: str = "https://api.chatwork.com/v2"
        self.headers = {
            "X-ChatWorkToken": os.getenv("CHATWORK_TOKEN"),
        }
        self.message = message
        self.to_room_id = self.get_room_id(room_name)

    def send_message(self) -> None:
        ep = f"/rooms/{self.to_room_id}/messages"
        data = {
            'body': self.message
        }
        res = requests.post(self.api_url + ep, headers=self.headers, data=data)
        assert res.status_code == 200

    def get_room_id(self, room_name: str) -> int:
        ep = "/rooms"
        res = requests.get(self.api_url + ep, headers=self.headers)
        assert res.status_code == 200
        target = list(filter(lambda x: x["name"] == room_name, res.json()))[0]
        return target["room_id"]


class Twitter:
    def __init__(self, message: str) -> None:
        auth = tweepy.OAuthHandler(
            os.getenv("TWITTER_CONSUMER_KEY"),
            os.getenv("TWITTER_CONSUMER_KEY_SECRET")
        )
        auth.set_access_token(
            os.getenv("TWITTER_ACCESSTOKEN"),
            os.getenv("TWITTER_ACCESSTOKEN_SECRET")
        )
        self.api = tweepy.API(auth)
        self.message = message

    def tweet(self) -> None:
        self.api.update_status(self.message)


class Discord(discord.Client):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    async def on_ready(self):
        channel = await self.fetch_channel(os.getenv("DISCORD_CHANNEL_ID"))
        await channel.send(self.message)
        await self.logout()


if __name__ == "__main__":
    with open(os.path.dirname(os.path.abspath(__file__)) + "/data.txt") as f:
        is_working = int(f.read())
    if is_working == 0:
        message = ["おはようございます", "しゅっきん", "しゅっきん"]
        print("出勤")
        is_working = 1
    else:
        message = [
            "お疲れさまでした", "いぇったいきん\N{WHITE UP POINTING INDEX}\ufe0f", "たいきん"]
        print("退勤")
        is_working = 0
    cw = Chatwork(os.getenv("CHATWORK_ROOM_NAMEs"), message[0])
    cw.send_message()
    tw = Twitter(message[1])
    tw.tweet()
    dc = Discord(message[2])
    dc.run(os.getenv("DISCORD_TOKEN"))
    with open(os.path.dirname(os.path.abspath(__file__)) + "/data.txt", "w") as f:
        f.write(str(is_working))
