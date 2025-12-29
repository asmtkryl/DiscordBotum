import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import keep_alive

# Çevresel değişkenleri yükle
load_dotenv()

# Intent ayarları (Mesajları okuyabilmesi için şart)
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriğini okuma yetkisi
intents.members = True          # Üyeleri görme yetkisi

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    
    # Cogs klasörünü kontrol et ve yükle
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'📂 Eklenti yüklendi: {filename}')
                except Exception as e:
                    print(f'❌ {filename} yüklenirken hata oluştu: {e}')
    else:
        print("⚠️ 'cogs' klasörü bulunamadı!")

# Basit bir deneme komutu (Botun çalışıp çalışmadığını anlamak için)
@bot.command()
async def deneme(ctx):
    await ctx.send('Bot başarıyla çalışıyor ve mesaj gönderiyor! 🚀')

# Web sunucusunu başlat
keep_alive.keep_alive()

# Render'daki 'TOKEN' anahtarı ile botu çalıştır
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ HATA: TOKEN bulunamadı! Render Environment Variables kısmını kontrol et.")

