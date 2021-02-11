import random
from datetime import datetime

import discord
from dateutil.rrule import rrule, HOURLY
from discord.ext import commands, tasks

from config import TOKEN

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

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

class GenshinAccountability(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.next_run = datetime.now()
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

        guild = self.bot.get_guild(689238357670232083)
        if not guild:
            return

        banned_users = tuple()
        if genzai.hour == 22:
            banned_users = (148954595350151168, 325944609463205888)
        elif genzai.hour == 1:
            banned_users = (417473397769895951, )
        elif self.banned_user_override:
            banned_users = (self.banned_user_override, )
            self.banned_user_override = None

        banned_channels = {780579621040422932, 698338845502078987}
        for user_id in banned_users:
            member = await guild.fetch_member(user_id)
            if member and member.voice and member.voice.channel:
                if member.voice.channel.id in banned_channels:
                    await self.bot.get_channel(802399940109664296).send(random.choice([
                        f"<@!{user_id}> daily reminder to stop playing Genshin!!",
                        f"<@!{user_id}> didn't you say you were going to stop playing games?",
                        f"I sure hope you've logged off of Genshin <@!{user_id}>",
                        f"<@!{user_id}> it's time to remove yourself from Genshin",
                        f"<@!{user_id}> have you forgotten about your accountability goals?",
                        f"<@!{user_id}> bruh.",
                    ]))

    @commands.command(name='shame')
    async def test_shame_bot(self, ctx):
        self.banned_user_override = ctx.author.id
        self.next_run = datetime.now()


bot.add_cog(GenshinAccountability(bot))
bot.run(TOKEN)
