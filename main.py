import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Intent'leri açıyoruz
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')
    # Cogs klasöründeki eklentileri yükle
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'{filename} yüklendi.')

bot.run(os.getenv('DISCORD_TOKEN'))