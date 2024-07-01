import discord, os
from discord.ext import commands

from main import PointGeter


intents = discord.Intents.default()
intents.message_content = True

token = os.getenv('DISCORD_TEST_BOT_TOKEN', None)
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")

@bot.command()
@commands.has_permissions(administrator=True)
async def synccommands(ctx):
    await bot.tree.sync()
    await ctx.send("同步完成")


@bot.hybrid_command()
async def get_point(ctx: commands.Context, student_number: str, password: str):
    await ctx.interaction.response.defer(ephemeral=True)
    getter = PointGeter()
    getter.proccess(number=student_number, password=password)
    await ctx.interaction.followup.send(f'{getter.result}', ephemeral=True)  

if token:
    bot.run(token=token)
else:
    print("there is not token")
