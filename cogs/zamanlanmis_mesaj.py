import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import asyncio
import re

class ZamanlanmisMesaj(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_name = "zamanlanmis_mesajlar.db"
        self.setup_db()
        self.zamanlayici_kontrol.start()
        self.sabit_saat_kontrol.start()

    def setup_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Periyotlu mesajlar tablosu
        c.execute('''CREATE TABLE IF NOT EXISTS periyotlu_mesajlar
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER, start_time TEXT, interval INTEGER, next_run REAL, content TEXT)''')
        # Sabit saatli mesajlar tablosu
        c.execute('''CREATE TABLE IF NOT EXISTS sabit_mesajlar
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER, saat TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def cog_unload(self):
        self.zamanlayici_kontrol.cancel()
        self.sabit_saat_kontrol.cancel()

    async def uclu_mesaj_gonder(self, channel, content):
        """Mesajı 3 kere gönderir ve 10 dakika sonra siler."""
        for _ in range(3):
            try:
                await channel.send(content, delete_after=600) # 600 saniye = 10 dakika
                await asyncio.sleep(2) # Mesajlar arasında çok kısa bekleme (opsiyonel)
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")

    # --- KOMUTLAR ---

    @commands.command(name="mesaj-baslat")
    async def mesaj_baslat(self, ctx, kanal: discord.TextChannel, baslangic_saati: str, aralik: int, *, mesaj: str):
        """!mesaj-baslat #kanal 14:30 60 Merhaba Dünya"""
        try:
            now = datetime.datetime.now()
            hour, minute = map(int, baslangic_saati.split(':'))
            start_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if start_dt < now:
                start_dt += datetime.timedelta(days=1)

            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("INSERT INTO periyotlu_mesajlar (channel_id, start_time, interval, next_run, content) VALUES (?, ?, ?, ?, ?)",
                      (kanal.id, baslangic_saati, aralik, start_dt.timestamp(), mesaj))
            conn.commit()
            conn.close()
            await ctx.send(f"✅ Periyotlu mesaj kuruldu: {kanal.mention} | Başlangıç: {baslangic_saati} | Aralık: {aralik}dk")
        except Exception as e:
            await ctx.send(f"❌ Hata: Parametreleri kontrol edin. Örn: `!mesaj-baslat #kanal 14:30 60 Mesaj`")

    @commands.command(name="sabit-mesaj")
    async def sabit_mesaj(self, ctx, kanal: discord.TextChannel, saat: str, *, mesaj: str):
        """!sabit-mesaj #kanal 18:00 Bu bir sabit mesajdır"""
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', saat):
            return await ctx.send("❌ Geçersiz saat formatı! (Örn: 18:00)")

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO sabit_mesajlar (channel_id, saat, content) VALUES (?, ?, ?)", (kanal.id, saat, mesaj))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Sabit mesaj kuruldu: {kanal.mention} kanalına her gün saat **{saat}**'de 3 kez atılacak.")

    @commands.command(name="sabit-listele")
    async def sabit_listele(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, channel_id, saat, content FROM sabit_mesajlar")
        rows = c.fetchall()
        conn.close()

        if not rows: return await ctx.send("📭 Sabit mesaj yok.")
        
        embed = discord.Embed(title="📌 Sabit Mesaj Listesi", color=discord.Color.green())
        for row in rows:
            embed.add_field(name=f"ID: {row[0]} | Saat: {row[2]}", value=f"Kanal: <#{row[1]}>\nMesaj: {row[3][:50]}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="mesaj-liste")
    async def mesaj_liste(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, channel_id, interval, content FROM periyotlu_mesajlar")
        rows = c.fetchall()
        conn.close()

        if not rows: return await ctx.send("📭 Periyotlu mesaj yok.")

        embed = discord.Embed(title="⏳ Periyotlu Mesaj Listesi", color=discord.Color.orange())
        for row in rows:
            embed.add_field(name=f"ID: {row[0]} | Aralık: {row[2]}dk", value=f"Kanal: <#{row[1]}>\nMesaj: {row[3][:50]}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="sabit-sil")
    async def sabit_sil(self, ctx, id: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM sabit_mesajlar WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ {id} numaralı sabit mesaj silindi.")

    @commands.command(name="mesaj-sil")
    async def mesaj_sil(self, ctx, id: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM periyotlu_mesajlar WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ {id} numaralı periyotlu mesaj silindi.")

    # --- DÖNGÜLER ---

    @tasks.loop(seconds=30)
    async def zamanlayici_kontrol(self):
        now_ts = datetime.datetime.now().timestamp()
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, channel_id, interval, content FROM periyotlu_mesajlar WHERE next_run <= ?", (now_ts,))
        
        for row in c.fetchall():
            msg_id, chan_id, interval, content = row
            channel = self.bot.get_channel(chan_id)
            if channel:
                await self.uclu_mesaj_gonder(channel, content)
            
            new_next_run = datetime.datetime.now().timestamp() + (interval * 60)
            c.execute("UPDATE periyotlu_mesajlar SET next_run = ? WHERE id = ?", (new_next_run, msg_id))
        
        conn.commit()
        conn.close()

    @tasks.loop(seconds=60)
    async def sabit_saat_kontrol(self):
        simdi = datetime.datetime.now().strftime("%H:%M")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT channel_id, content FROM sabit_mesajlar WHERE saat = ?", (simdi,))
        
        for row in c.fetchall():
            chan_id, content = row
            channel = self.bot.get_channel(chan_id)
            if channel:
                await self.uclu_mesaj_gonder(channel, content)
        
        conn.close()

    @zamanlayici_kontrol.before_loop
    @sabit_saat_kontrol.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ZamanlanmisMesaj(bot))
