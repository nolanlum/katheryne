import asyncio
import io
import os
import os.path
import re
from datetime import date

import discord
from discord.ext import commands
from discord.oggparse import OggStream
from discord.player import AudioSource

from . import baerritos
from . import yoink
from . import bot
from .config import TOKEN


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
**!yoink <emoji> <name>** - Yoink an emoji
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

@bot.command(name='moshi')
async def moshi(ctx):
    response = 'https://twitter.com/Giruyong/status/1442406252567412740'
    await ctx.send(response)

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

class TsugaruKaikyou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if baerritos.BUTTON_ID in [x.id for x in message.stickers]:
            if not message.author.voice or not message.author.voice.channel:
                return
            vc = await message.author.voice.channel.connect()

            try:
                done = asyncio.Event()
                vc.play(OpusAudioSource('wav/TsugaruKaikyouFuyugeshiki.opus'), after=lambda ex: done.set())
                await done.wait()
            finally:
                if vc.is_connected():
                    await vc.disconnect()

async def setup():
    await bot.add_cog(TsugaruKaikyou(bot))
    await bot.add_cog(yoink.Yoinker(bot))

bot.setup_hook = setup
bot.run(TOKEN)
