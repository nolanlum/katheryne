from discord.ext import commands

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

