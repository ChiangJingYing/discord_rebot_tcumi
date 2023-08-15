import discord
from discord.ext import commands
from main import PointGeter


intents = discord.Intents.default()
intents.message_content = True

token = 'MTEzNzcxMzk3MDU4OTk5MTAzMw.G4odhw.J8GsU1b8ZSOkVLM0hZo0yGqi1-QSezZ1ZVFf_s'

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
@commands.has_permissions(administrator=True)
async def synccommands(ctx):
    await bot.tree.sync()
    await ctx.send("同步完成")


@bot.hybrid_command()
async def get_point(ctx, student_number: str, password: str):
    await ctx.send("Searching...", delete_after=4.0,ephemeral=True)
    getter = PointGeter()
    getter.proccess(number=student_number, password=password)
    await ctx.send(f'{getter.result}', ephemeral=True)

bot.run(token=token)
