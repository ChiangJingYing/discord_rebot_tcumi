import asyncio

import discord
import os

from async_timeout import timeout
from discord.ext import commands

from main import PointGeter

intents = discord.Intents.default()
intents.message_content = True

token = os.getenv('DISCORD_BOT_TOKEN', None)
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

@bot.tree.command(name="point")
async def point(interaction: discord.Interaction):
    class PointModal(discord.ui.Modal, title='Point Information'):
        student_id = discord.ui.TextInput(
            label="學號",
            placeholder="輸入學號",
            custom_id="student_id",
            min_length=9,
            max_length=9
        )
        password = discord.ui.TextInput(
            label="密碼",
            placeholder="輸入密碼",
            custom_id="password",
            min_length=1,
            max_length=30,
        )

        async def on_submit(self, interaction: discord.Interaction):
            # Defer the response immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)

            # Extract form data
            for component in interaction.data['components']:
                component = component['components'][0]
                if component['custom_id'] == 'student_id':
                    self.student_id = component['value']
                elif component['custom_id'] == 'password':
                    self.password = component['value']

            try:
                # Process the point getting operation
                getter = PointGeter()
                getter.proccess(number=self.student_id, password=self.password)

                # Send the follow-up message with results
                await interaction.followup.send(
                    content=f'Thank you for your submission, {interaction.user.mention}!\n{getter.result[0]}',
                    file=discord.File(fp=getter.result[1], filename="紀錄表.xlsx"),
                    ephemeral=True
                )

                # Clean up the file after sending
                getter.result[1].unlink()

            except Exception as e:
                # Handle any errors that might occur during processing
                await interaction.followup.send(
                    content=f"An error occurred: {str(e)}",
                    ephemeral=True
                )

    modal = PointModal()
    await interaction.response.send_modal(modal)


@bot.hybrid_command()
async def get_point(ctx: commands.Context, student_number: str, password: str):
    await ctx.interaction.response.defer(ephemeral=True)
    getter = PointGeter()
    getter.proccess(number=student_number, password=password)
    await ctx.interaction.followup.send(f'{getter.result[0]}', ephemeral=True)

if token:
    bot.run(token=token)
else:
    print("there is not token")
