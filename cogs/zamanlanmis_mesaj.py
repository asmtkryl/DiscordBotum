import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import re
import asyncio

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
        # Aralıklarla atılan mesajlar tablosu
        c.execute('''CREATE TABLE IF NOT EXISTS mesajlar
                     (channel_id INTEGER, interval INTEGER, next_run REAL, content TEXT)''')
        # Sabit saatlerde atılan mesajlar tablosu
        c.execute('''CREATE TABLE IF NOT EXISTS sabit_mesajlar
                     (channel_id INTEGER, saat TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def cog_unload(self):
        self.zamanlayici_kontrol.cancel()
        self.sabit_saat_kontrol.cancel()

    async def akilli_ayristir(self, ctx, args):
        channel = ctx.channel 
        interval = None
        start_time_obj = None
        message_parts = []
        used_indices = []

        for i, arg in enumerate(args):
            if i in used_indices: continue
            try:
                converter = commands.TextChannelConverter()
                found_channel = await converter.convert(ctx, arg)
                channel = found_channel
                used_indices.append(i)
            except: pass

        for i, arg in enumerate(args):
            if i in used_indices: continue
            clean_arg = arg.replace('(', '').replace(')', '')
            if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', clean_arg):
                now = datetime.datetime.now()
                hour, minute = map(int, clean_arg.split(':'))
                start_time_obj = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                used_indices.append(i)
                break

        for i, arg in enumerate(args):
            if i in used_indices: continue
            if arg.isdigit() and interval is None:
                interval = int(arg)
                used_indices.append(i)
                break
        
        for i, arg in enumerate(args):
            if i not in used_indices:
                message_parts.append(arg)
        
        full_message = " ".join(message_parts)
        return channel, interval, start_time_obj, full_message

    # --- KOMUT 1: ARALIKLI MESAJ ---
    @commands.command(name="mesaj-baslat")
    async def mesaj_baslat(self, ctx, *args):
        channel, interval, start_time, content = await self.akilli_ayristir(ctx, args)
        if interval is None or not content:
            await ctx.send("❌ Hata: `!mesaj-baslat #kanal 30 Mesaj` şeklinde yazın.")
            return

        now = datetime.datetime.now()
        next_run = start_time if start_time and start_time > now else now
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM mesajlar WHERE channel_id = ?", (channel.id,))
        c.execute("INSERT INTO mesajlar VALUES (?, ?, ?, ?)", (channel.id, interval, next_run.timestamp(), content))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Döngü kuruldu: {channel.mention} | ⏱️ {interval}dk")

    # --- KOMUT 2: SABİT SAAT MESAJI ---
    @commands.command(name="sabit-kur")
    async def sabit_kur(self, ctx, saat: str, *, mesaj: str):
        """Örn: !sabit-kur 18:00 Bu bir akşam mesajıdır."""
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', saat):
            await ctx.send("❌ Geçersiz saat formatı! Örn: `18:00` veya `09:30`")
            return

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO sabit_mesajlar VALUES (?, ?, ?)", (ctx.channel.id, saat, mesaj))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Her gün saat **{saat}** için mesaj kuruldu!")

    @commands.command(name="sabit-liste")
    async def sabit_liste(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT saat, content FROM sabit_mesajlar WHERE channel_id = ?", (ctx.channel.id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            await ctx.send("📭 Bu kanalda sabit saatli mesaj yok.")
            return
        liste = "\n".join([f"• **{r[0]}**: {r[1][:20]}..." for r in rows])
        await ctx.send(f"📋 **Sabit Saatli Mesajlar:**\n{liste}")

    # --- DÖNGÜ 1: ARALIKLI KONTROL ---
    @tasks.loop(seconds=20)
    async def zamanlayici_kontrol(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        now_ts = datetime.datetime.now().timestamp()
        c.execute("SELECT rowid, channel_id, interval, content FROM mesajlar WHERE next_run <= ?", (now_ts,))
        for row in c.fetchall():
            row_id, chan_id, interval, content = row
            channel = self.bot.get_channel(chan_id) or await self.bot.fetch_channel(chan_id)
            if channel:
                await channel.send(content, delete_after=600) # 10 dk sonra siler
            next_run_new = datetime.datetime.now().timestamp() + (interval * 60)
            c.execute("UPDATE mesajlar SET next_run = ? WHERE rowid = ?", (next_run_new, row_id))
        conn.commit()
        conn.close()

    # --- DÖNGÜ 2: SABİT SAAT KONTROL ---
    @tasks.loop(seconds=60)
    async def sabit_saat_kontrol(self):
        simdi = datetime.datetime.now().strftime("%H:%M")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT channel_id, content FROM sabit_mesajlar WHERE saat = ?", (simdi,))
        for row in c.fetchall():
            chan_id, content = row
            channel = self.bot.get_channel(chan_id) or await self.bot.fetch_channel(chan_id)
            if channel:
                await channel.send(content, delete_after=600)
        conn.close()

    @zamanlayici_kontrol.before_loop
    @sabit_saat_kontrol.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ZamanlanmisMesaj(bot))
