import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import keep_alive
import datetime

# --- SAAT DİLİMİ AYARI ---
# Render/VDS gibi sunucularda saati Türkiye'ye sabitler
os.environ['TZ'] = 'Europe/Istanbul' 

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    # Bot başladığında sadece 1 kere çalışır ve eklentileri yükler
    async def setup_hook(self):
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f'📂 Eklenti yüklendi: {filename}')
                    except Exception as e:
                        print(f'❌ {filename} yüklenirken hata oluştu: {e}')
        else:
            print("⚠️ 'cogs' klasörü bulunamadı!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    print(f'⏰ Sunucu Saati: {datetime.datetime.now().strftime("%H:%M")}')

@bot.command()
async def deneme(ctx):
    await ctx.send('Bot başarıyla çalışıyor! 🚀')

# Web sunucusunu başlat
keep_alive.keep_alive()

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ HATA: TOKEN bulunamadı!")
