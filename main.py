#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import random

import discord
import discord.app_commands
from discord.ext import tasks

from server import keep_alive

discord_token = os.environ["DISCORD_TOKEN"]
main_channel_id = int(os.environ["MAIN_CHANNEL_ID"])
bot_channel_id = int(os.environ["BOT_CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True


class Pengan(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")
        await self.change_presence(activity=discord.Game(name="!!help", type=1))
        await client.get_channel(bot_channel_id).send(f"We have logged in as {self.user}")

        # async for message in client.get_channel().history(limit=20):
        #     print(message.content)
        # await client.get_channel().send()

        loop.start()

    async def on_message(self, message: discord.Message):
        print(f"""
On {message.channel}, {message.channel.guild} ({message.channel.id})
{message.author}: {message.content}""")
        if message.author == self.user:
            return
        if message.content == "!!help":
            await message.channel.send("ヘルプ: !!help")

        if "ohayo" in message.content.lower():
            await message.add_reaction("\N{Black Heart}")
        if "oyasumi" in message.content.lower():
            await message.add_reaction("<:emoji_2:1074290659135066163>")
        if "geosta" in message.content.lower() or "努力 未来 a geoffroyi star" in message.content.lower():
            await message.add_reaction(
                "<:otonadechi:1065560408934592582>" if random.random() < 0.5 else "<:PENGIN_LV98:1097096256939114517>"
            )
        if "充 電 し な き ゃ 　敵 の 命 で ね" in message.content.lower():
            await message.add_reaction("\N{Black Heart}")


@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now()
    if (now.hour, now.minute) == (22, 0):
        await client.get_channel(main_channel_id).send("ohayo")
    elif (now.hour, now.minute) == (13, 0):
        await client.get_channel(main_channel_id).send("oyasumi")
    elif (now.hour, now.minute) == (15, 0):
        await client.get_channel(main_channel_id).send(
            "geosta" if random.random() < 0.9 else "努力 未来 a geoffroyi star"
        )


client = Pengan()


keep_alive()

client.run(discord_token)
