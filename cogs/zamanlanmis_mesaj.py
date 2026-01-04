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

    def tr_saati_getir(self):
        """Türkiye saatini (UTC+3) döndürür."""
        return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)

    def setup_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # guild_id eklendi: Sunucuların verileri ayrıştırıldı
        c.execute('''CREATE TABLE IF NOT EXISTS periyotlu_mesajlar
                     (id INTEGER PRIMARY KEY, guild_id INTEGER, channel_id INTEGER, interval INTEGER, next_run REAL, content TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sabit_mesajlar
                     (id INTEGER PRIMARY KEY, guild_id INTEGER, channel_id INTEGER, saat TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def bos_id_bul(self, tablo_adi):
        """Silinen ID'lerin yerini doldurmak için en küçük boş ID'yi bulur."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(f"SELECT id FROM {tablo_adi} ORDER BY id ASC")
        mevcut_id_ler = [row[0] for row in c.fetchall()]
        conn.close()
        
        yeni_id = 1
        for m_id in mevcut_id_ler:
            if m_id == yeni_id:
                yeni_id += 1
            else:
                break
        return yeni_id

    async def uclu_mesaj_gonder(self, channel, content):
        """3 kez mesaj atar ve her birini 10 dakika (600sn) sonra siler."""
        for _ in range(3):
            try:
                await channel.send(content, delete_after=600)
                await asyncio.sleep(2) 
            except:
                pass

    # --- KOMUTLAR ---

    @commands.command(name="mesaj-baslat")
    async def mesaj_baslat(self, ctx, kanal: discord.TextChannel, baslangic_saati: str, aralik: int, *, mesaj: str):
        try:
            tr_now = self.tr_saati_getir()
            hour, minute = map(int, baslangic_saati.split(':'))
            start_dt = tr_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if start_dt < tr_now:
                start_dt += datetime.timedelta(days=1)

            yeni_id = self.bos_id_bul("periyotlu_mesajlar")
            
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("INSERT INTO periyotlu_mesajlar (id, guild_id, channel_id, interval, next_run, content) VALUES (?, ?, ?, ?, ?, ?)",
                      (yeni_id, ctx.guild.id, kanal.id, aralik, start_dt.timestamp(), mesaj))
            conn.commit()
            conn.close()
            await ctx.send(f"✅ Periyotlu mesaj kuruldu! **ID: {yeni_id}** | Kanal: {kanal.mention} | Aralık: {aralik}dk")
        except:
            await ctx.send("❌ Hata! Format: `!mesaj-baslat #kanal 14:30 60 Mesaj`")

    @commands.command(name="sabit-mesaj")
    async def sabit_mesaj(self, ctx, kanal: discord.TextChannel, saat: str, *, mesaj: str):
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', saat):
            return await ctx.send("❌ Hata: Saat formatı 18:00 gibi olmalı.")

        yeni_id = self.bos_id_bul("sabit_mesajlar")

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO sabit_mesajlar (id, guild_id, channel_id, saat, content) VALUES (?, ?, ?, ?, ?)", 
                  (yeni_id, ctx.guild.id, kanal.id, saat, mesaj))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Sabit mesaj kuruldu! **ID: {yeni_id}** | Kanal: {kanal.mention} | Saat: {saat}")

    @commands.command(name="sabit-listele")
    async def sabit_listele(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Sadece bu sunucuya (guild_id) ait mesajları getir
        c.execute("SELECT id, channel_id, saat, content FROM sabit_mesajlar WHERE guild_id = ? ORDER BY id ASC", (ctx.guild.id,))
        rows = c.fetchall()
        conn.close()

        if not rows: return await ctx.send("📭 Bu sunucu için sabit mesaj yok.")
        
        embed = discord.Embed(title="📌 Sunucu Sabit Mesajları", color=discord.Color.blue())
        for r in rows:
            embed.add_field(name=f"ID: {r[0]} | Saat: {r[2]}", value=f"Kanal: <#{r[1]}>\nMesaj: {r[3][:50]}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="mesaj-liste")
    async def mesaj_liste(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Sadece bu sunucuya (guild_id) ait mesajları getir
        c.execute("SELECT id, channel_id, interval, content FROM periyotlu_mesajlar WHERE guild_id = ? ORDER BY id ASC", (ctx.guild.id,))
        rows = c.fetchall()
        conn.close()

        if not rows: return await ctx.send("📭 Bu sunucu için periyotlu mesaj yok.")
        
        embed = discord.Embed(title="⏳ Sunucu Periyotlu Mesajları", color=discord.Color.gold())
        for r in rows:
            embed.add_field(name=f"ID: {r[0]} | Aralık: {r[2]}dk", value=f"Kanal: <#{r[1]}>\nMesaj: {r[3][:50]}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="sabit-sil")
    async def sabit_sil(self, ctx, id: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Sadece bu sunucuya ait ID'yi sil (Güvenlik için guild_id kontrolü)
        c.execute("DELETE FROM sabit_mesajlar WHERE id = ? AND guild_id = ?", (id, ctx.guild.id))
        if conn.total_changes > 0:
            await ctx.send(f"✅ ID: {id} olan sabit mesaj silindi.")
        else:
            await ctx.send(f"❌ ID: {id} bulunamadı veya bu sunucuya ait değil.")
        conn.commit()
        conn.close()

    @commands.command(name="mesaj-sil")
    async def mesaj_sil(self, ctx, id: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM periyotlu_mesajlar WHERE id = ? AND guild_id = ?", (id, ctx.guild.id))
        if conn.total_changes > 0:
            await ctx.send(f"✅ ID: {id} olan periyotlu mesaj silindi.")
        else:
            await ctx.send(f"❌ ID: {id} bulunamadı veya bu sunucuya ait değil.")
        conn.commit()
        conn.close()

    # --- DÖNGÜLER ---

    @tasks.loop(seconds=30)
    async def zamanlayici_kontrol(self):
        tr_now_ts = self.tr_saati_getir().timestamp()
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, channel_id, interval, content FROM periyotlu_mesajlar WHERE next_run <= ?", (tr_now_ts,))
        
        for row in c.fetchall():
            msg_id, chan_id, interval, content = row
            channel = self.bot.get_channel(chan_id) or await self.bot.fetch_channel(chan_id)
            if channel:
                await self.uclu_mesaj_gonder(channel, content)
            
            new_next_run = self.tr_saati_getir().timestamp() + (interval * 60)
            c.execute("UPDATE periyotlu_mesajlar SET next_run = ? WHERE id = ?", (new_next_run, msg_id))
        
        conn.commit()
        conn.close()

    @tasks.loop(seconds=60)
    async def sabit_saat_kontrol(self):
        tr_simdi = self.tr_saati_getir().strftime("%H:%M")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT channel_id, content FROM sabit_mesajlar WHERE saat = ?", (tr_simdi,))
        
        for row in c.fetchall():
            chan_id, content = row
            channel = self.bot.get_channel(chan_id) or await self.bot.fetch_channel(chan_id)
            if channel:
                await self.uclu_mesaj_gonder(channel, content)
        conn.close()

    @zamanlayici_kontrol.before_loop
    @sabit_saat_kontrol.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ZamanlanmisMesaj(bot))
