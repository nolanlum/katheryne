import asyncio
import io
import os
import os.path
import random
import re
from datetime import datetime

import discord
from dateutil.rrule import rrule, HOURLY, DAILY
from discord.ext import commands, tasks
from discord.oggparse import OggStream
from discord.player import AudioSource

from . import bot
from .config import TOKEN

from .baerritos import BaerritoConstants

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='commands', aliases=['help'])
async def show_commands(ctx):
    embed = discord.Embed(
        title="Supported commands",
        description="""
**!himbo** - ELI5 himbo
**!think** - Big brain
**!pekothink** - Big brain peko
**!dispose** - A sexist picture targeting the fragile male ego
**!hornyjail** - Go to jail
**!hornyflag** - Flag on the play
**!bonksho** - Experience the wrath of the rock
**!maaya** - Best girl
""".strip()
    )
    await ctx.send(embed=embed)

@bot.command(name='maaya')
async def maaya(ctx):
    response = 'https://imgur.com/HEqT9UB'
    await ctx.send(response)

@bot.command(name='think')
async def think(ctx):
    await ctx.send(file=discord.File('img/share_if_you_dont_think.jpg'))

@bot.command(name='pekothink')
async def pekothink(ctx):
    await ctx.send(file=discord.File('img/share_if_you_dont_think_peko.jpg'))

@bot.command(name='dispose')
async def dispose(ctx):
    await ctx.send(file=discord.File('img/dispose.jpg'))

@bot.command(name='himbo')
async def himbo(ctx):
    response = 'https://twitter.com/rice_deity/status/1213290130368319488'
    await ctx.send(response)

@bot.command(name='hornyjail')
async def hornyjail(ctx):
    await ctx.send(file=discord.File('img/hornyjail.jpg'))

@bot.command(name='hornyflag')
async def hornyflag(ctx):
    await ctx.send(file=discord.File('img/hornyflag.jpg'))

@bot.command(name='bonksho')
async def bonksho(ctx):
    await ctx.send(file=discord.File('img/tendo_bonksho.jpg'))

class OpusAudioSource(AudioSource):
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self.audio_bytes = f.read()
        self.packet_iter = OggStream(io.BytesIO(self.audio_bytes)).iter_packets()

    def is_opus(self):
        return True

    def read(self):
        return next(self.packet_iter, b'')

PLAY_COMMAND_PATTERN = re.compile('!p(?:lay)? (?P<name>[a-z0-9_-]+)')
@bot.command(name='p')
async def play_audio(ctx):
    match = PLAY_COMMAND_PATTERN.match(ctx.message.content)
    if not match:
        return

    audiofile_name = f"wav/{match.group('name')}.opus"
    if not os.path.exists(audiofile_name):
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        return
    vc = await ctx.author.voice.channel.connect()

    try:
        done = asyncio.Event()
        vc.play(OpusAudioSource(audiofile_name), after=lambda ex: done.set())
        await done.wait()
    finally:
        if vc.is_connected():
            await vc.disconnect()

@bot.command(name='p?')
async def list_audio_files(ctx):
    embed = discord.Embed(
        title="Available (meme) audio clips",
        description=", ".join(f"`{f[:-5]}`" for f in sorted(os.listdir('wav/')) if f.endswith('.opus'))
    )
    await ctx.send(embed=embed)

class GenshinAccountability(commands.Cog):
    BC = BaerritoConstants()

    def __init__(self, bot):
        self.bot = bot
        self.next_run = self.get_next_run()
        self.banned_user_override = None

    def cog_unload(self):
        self.check_online.stop()

    def get_next_run(self):
        return rrule(HOURLY, byminute=30, bysecond=0).after(datetime.now())

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_online.is_running():
            self.check_online.start()

    @tasks.loop(seconds=1)
    async def check_online(self):
        genzai = datetime.now()
        if genzai < self.next_run:
            return
        self.next_run = self.get_next_run()

        guild = self.bot.get_guild(self.BC.BAERRITOS_GUILD_ID)
        if not guild:
            return

        banned_users = tuple()
        if self.banned_user_override:
            banned_users = (self.banned_user_override, )
            self.banned_user_override = None
        elif genzai.hour == 22:
            banned_users = self.BC.BAERRITOS_GENSHIN_ACCOUNTABILITY_22
        elif genzai.hour == 1:
            banned_users = self.BC.BAERRITOS_GENSHIN_ACCOUNTABILITY_25

        for user_id in banned_users:
            member = await guild.fetch_member(user_id)
            if member and member.voice and member.voice.channel:
                if member.voice.channel.id in self.BC.BAERRITOS_GENSHIN_CHANNELS:
                    reminder = random.choice([
                        f"<@!{user_id}> daily reminder to stop playing Genshin!!",
                        f"<@!{user_id}> didn't you say you were going to stop playing games?",
                        f"I sure hope you've logged off of Genshin <@!{user_id}>",
                        f"<@!{user_id}> it's time to remove yourself from Genshin",
                        f"<@!{user_id}> have you forgotten about your accountability goals?",
                        f"<@!{user_id}> bruh.",
                    ])
                    await self.bot.get_channel(self.BC.BAERRITOS_ACCOUNTABILITY_CHANNEL).send(reminder)

    @commands.command(name='shame')
    async def test_shame_bot(self, ctx):
        self.banned_user_override = ctx.author.id
        self.next_run = datetime.now()

class GenshinWebLogin(commands.Cog):
    BC = BaerritoConstants()

    def __init__(self, bot):
        self.bot = bot
        self.next_run = self.get_next_run()
        self.test_user = None

    def cog_unload(self):
        self.check_online.stop()

    def get_next_run(self):
        return rrule(DAILY, byhour=2, byminute=20, bysecond=20).after(datetime.now())

    def precondition(self):
        if self.test_user:
            return True

        genzai = datetime.now()
        if genzai < self.next_run:
            return False
        self.next_run = self.get_next_run()

        guild = self.bot.get_guild(self.BC.BAERRITOS_GUILD_ID)
        if not guild:
            return False

        return True

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_online.is_running():
            self.check_online.start()

    @tasks.loop(seconds=5)
    async def check_online(self):
        if not self.precondition():
            return

        checkin_user_ids = list()
        if self.test_user:
            checkin_user_ids = [self.test_user]
            self.test_user = None
        else:
            checkin_user_ids = self.BC.BAERRITOS_GENSHIN_CHECKIN_USERS

        online_members = ['<@!{0}>'.format(user_id) for user_id in checkin_user_ids]
        reminder_members = " ".join(online_members)
        reminder = f"{reminder_members}: 星と深淵を目指せ！ A reminder to check in online at https://webstatic-sea.mihoyo.com/ys/event/signin-sea/index.html?act_id=e202102251931481&lang=en-us"
        await self.bot.get_channel(self.BC.BAERRITOS_GAMES_CHANNEL).send(reminder)

    @commands.command(name='genshinlogin')
    async def test_login_reminder(self, ctx):
        self.test_user = ctx.author.id

bot.add_cog(GenshinAccountability(bot))
bot.add_cog(GenshinWebLogin(bot))
bot.run(TOKEN)
