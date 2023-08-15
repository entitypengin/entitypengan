#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import random

import discord
from discord.ext import tasks
from replit import db

from constants import (
    Channels,
    DISCORD_TOKEN,
    SHEET_CREDS,
    SPREADSHEET_ID,
    Status,
)
import radio
from server import keep_alive


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Pengan(discord.Client):
    status: Status = Status.EXCEPTION

    main_channel: discord.TextChannel
    welcome_channel: discord.TextChannel
    radio_answers_channel: discord.TextChannel
    bot_channel: discord.TextChannel

    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self) -> None:
        self.main_channel = self.get_channel(Channels.MAIN_CHANNEL_ID)
        self.radio_answers_channel = self.get_channel(Channels.RADIO_ANSWERS_CHANNEL_ID)
        self.bot_channel = self.get_channel(Channels.BOT_CHANNEL_ID)

        last_working = datetime.datetime.fromtimestamp(db["last_working"], datetime.timezone.utc)

        for guild in self.guilds:
            for channel in guild.channels:
                if hasattr(channel, "history"):
                    async for message in channel.history(after=last_working):
                        await self.reaction(message)

        print(f"""We have logged in as {self.user}
""")
        await self.bot_channel.send(f"We have logged in as {self.user}")

        """        async for message in client.get_channel().history(limit=20):
            print(message.content)
        await self.main_channel.send("これ実は1/10の確率でgeosta全文言うようにしてるんだよね")
        await self.main_channel.guild.get_member(self.user.id).edit(nick=None)
        """

        loop.start()

    async def on_member_join(self, member: discord.Member) -> None:
        await member.guild.system_channel.send(f"""{member.mention}がやってきました！
現在のメンバーは{member.guild.member_count}人です""")

    async def on_member_remove(self, member: discord.Member) -> None:
        await member.guild.system_channel.send(f"""{member.mention}が退出しました
現在のメンバーは{member.guild.member_count}人です""")

    async def on_message(self, message: discord.Message) -> None:
        print(f"""On {message.channel}, {message.channel.guild} ({message.channel.id})
{message.author}: {message.content}
""")
        if message.author == self.user:
            return
        if message.content == "!!help":
            await message.channel.send("ヘルプ: !!help")
        if message.content.startswith("!!debug"):
            arg = message.content.split()[1]
            if arg == "ohayo":
                self.status = Status.OHAYO
                await self.update_presence()
                await message.channel.send("OK")
            elif arg == "oyasumi":
                self.status = Status.OYASUMI
                await self.update_presence()
                await message.channel.send("OK")
            elif arg == "charge":
                self.status = Status.CHARGE
                await self.update_presence()
                await message.channel.send("OK")
            elif arg == "geosta":
                self.status = Status.GEOSTA
                await self.update_presence()
                await message.channel.send("OK")

        await self.reaction(message)

    async def reaction(self, message: discord.Message):
        if "ohayo" in message.content.lower():
            await message.add_reaction("\U0001f5a4")
        if "oyasumi" in message.content.lower():
            await message.add_reaction("<:emoji_2:1074290659135066163>")
        if "geosta" in message.content.lower() or "努力 未来 a geoffroyi star" in message.content.lower():
            await message.add_reaction("<:PENGIN_LV98:1097096256939114517>")
        if (
            "ecchi" in message.content.lower()
            or "えっち" in message.content.lower()
            or "エッチ" in message.content.lower()
        ):
            await message.add_reaction("<:otonadechi:1065560408934592582>")
        if "充 電 し な き ゃ 　敵 の 命 で ね" in message.content.lower():
            if self.status == Status.OYASUMI:
                self.status = Status.CHARGE
            await message.add_reaction("\U0001f5a4")
        if "10 years in the joint made you a fucking pussy" in message.content.lower():
            await message.add_reaction("<:10yearsinthejointmadeyouafucking:1140457966009593977>")

    async def update_status(self, now) -> None:
        if 13 <= now.hour < 15:
            if self.status != Status.CHARGE:
                self.status = Status.OYASUMI
        elif 15 <= now.hour < 22:
            self.status = Status.GEOSTA
        else:
            self.status = Status.OHAYO

        if now.minute == 0:
            if now.hour == 22:
                await self.main_channel.send("ohayo")
            elif now.hour == 1:
                await self.main_channel.send("10 years in the joint made you a fucking pussy")
            elif now.hour == 13:
                await self.main_channel.send("oyasumi")
            elif now.hour == 15:
                await self.main_channel.send(
                    "geosta" if random.random() < 0.9 else "努力 未来 a geoffroyi star"
                )

    async def update_presence(self) -> None:
        if self.status == Status.OHAYO:
            await client.change_presence(
                status=discord.Status.online, activity=discord.Game(name="!!help", type=1)
            )
        elif self.status == Status.OYASUMI:
            await client.change_presence(
                status=discord.Status.idle, activity=discord.Game(name="爆発", type=1)
            )
        elif self.status == Status.CHARGE:
            await client.change_presence(
                status=discord.Status.dnd, activity=discord.Game(name="充電", type=1)
            )
        elif self.status == Status.GEOSTA:
            await client.change_presence(
                status=discord.Status.dnd, activity=discord.Game(name="努力", type=1)
            )

    async def check_radio_answers(self) -> None:
        answers = radio.get_answers(SPREADSHEET_ID, SHEET_CREDS)
        radio_answers_count = len(answers)
        if 0 < (diff := radio_answers_count - db["radio_answers_count"]):
            db["radio_answers_count"] = radio_answers_count
            new = answers[-diff:]
            for answer in new:
                await self.radio_answers_channel.send(f"""{answer[0]}
ラジオネーム: {answer[1]}
性別: {answer[2]}
年代: {answer[3]}
地域: {answer[4]}

{answer[5]}""")


@tasks.loop(seconds=60)
async def loop() -> None:
    try:
        now = datetime.datetime.now(datetime.timezone.utc)

        print(now)

        db["last_working"] = now.timestamp()

        await client.update_status(now)
        await client.update_presence()

        if now.minute % 2 == 0:
            try:
                await client.check_radio_answers()
            except BaseException as e:
                print(e)

    except BaseException as e:
        print(e)

client = Pengan()

keep_alive()

client.run(DISCORD_TOKEN)
