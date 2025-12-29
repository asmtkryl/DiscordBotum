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

    def setup_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mesajlar
                     (channel_id INTEGER, interval INTEGER, next_run REAL, content TEXT)''')
        conn.commit()
        conn.close()

    def cog_unload(self):
        self.zamanlayici_kontrol.cancel()

    async def akilli_ayristir(self, ctx, args):
        channel = ctx.channel 
        interval = None
        start_time_obj = None
        message_parts = []
        used_indices = []

        for i, arg in enumerate(args):
            if not any(x in used_indices for x in [i]):
                try:
                    converter = commands.TextChannelConverter()
                    found_channel = await converter.convert(ctx, arg)
                    channel = found_channel
                    used_indices.append(i)
                    continue
                except:
                    pass

            if not any(x in used_indices for x in [i]):
                clean_arg = arg.replace('(', '').replace(')', '')
                if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', clean_arg):
                    now = datetime.datetime.now()
                    hour, minute = map(int, clean_arg.split(':'))
                    start_time_obj = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    used_indices.append(i)
                    continue

            if not any(x in used_indices for x in [i]):
                if arg.isdigit() and interval is None:
                    interval = int(arg)
                    used_indices.append(i)
                    continue
        
        for i, arg in enumerate(args):
            if i not in used_indices:
                message_parts.append(arg)
        
        full_message = " ".join(message_parts)
        return channel, interval, start_time_obj, full_message

    # DİKKAT: Burada @bot.command değil, @commands.command kullanılır!
    @commands.command(name="mesaj-baslat")
    async def mesaj_baslat(self, ctx, *args):
        if not args:
            await ctx.send("❌ Parametre girin. Örn: `!mesaj-baslat #chat 30 (14:30) Günaydın`")
            return

        channel, interval, start_time, content = await self.akilli_ayristir(ctx, args)

        if interval is None:
            await ctx.send("⚠️ **Hata:** Kaç dakikada bir atılacağı (sayı) bulunamadı.")
            return
        if not content:
            await ctx.send("⚠️ **Hata:** Mesaj içeriği yok.")
            return

        now = datetime.datetime.now()
        if start_time is None:
            next_run = now
            zaman_bilgisi = "Hemen"
        else:
            if start_time.hour == now.hour and start_time.minute == now.minute:
                next_run = now
                zaman_bilgisi = "Hemen"
            elif start_time < now:
                next_run = start_time + datetime.timedelta(days=1)
                zaman_bilgisi = f"Yarın {next_run.strftime('%H:%M')}"
            else:
                next_run = start_time
                zaman_bilgisi = f"Bugün {next_run.strftime('%H:%M')}"

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM mesajlar WHERE channel_id = ?", (channel.id,))
        c.execute("INSERT INTO mesajlar VALUES (?, ?, ?, ?)", 
                  (channel.id, interval, next_run.timestamp(), content))
        conn.commit()
        conn.close()

        await ctx.send(f"✅ **Kuruldu:** {channel.mention} | ⏱️ {interval}dk | 🚀 {zaman_bilgisi}")

    @commands.command(name="mesaj-sil")
    async def mesaj_sil(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM mesajlar WHERE channel_id = ?", (target_channel.id,))
        conn.commit()
        conn.close()
        await ctx.send(f"🗑️ {target_channel.mention} için döngü silindi.")

    @commands.command(name="mesaj-listele")
    async def mesaj_listele(self, ctx):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT channel_id, interval, next_run, content FROM mesajlar")
        rows = c.fetchall()
        conn.close()

        if not rows:
            await ctx.send("📭 Aktif mesaj yok.")
            return

        text = "**📋 Liste:**\n"
        for row in rows:
            chan_id, interval, next_ts, msg = row
            next_run_dt = datetime.datetime.fromtimestamp(next_ts)
            text += f"• <#{chan_id}> | {interval}dk | 🔜 {next_run_dt.strftime('%H:%M')} | `{msg[:15]}...`\n"
        
        await ctx.send(text)

    @tasks.loop(seconds=30)
    async def zamanlayici_kontrol(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        now_ts = datetime.datetime.now().timestamp()
        
        c.execute("SELECT rowid, channel_id, interval, content FROM mesajlar WHERE next_run <= ?", (now_ts,))
        gorevler = c.fetchall()

        for row in gorevler:
            row_id, chan_id, interval, content = row
            channel = self.bot.get_channel(chan_id)
            if channel:
                try:
                    await channel.send(content, delete_after=600)
                except:
                    pass
            
            next_run_new = now_ts + (interval * 60)
            c.execute("UPDATE mesajlar SET next_run = ? WHERE rowid = ?", (next_run_new, row_id))
        
        conn.commit()
        conn.close()

    @zamanlayici_kontrol.before_loop
    async def before_zamanlayici(self):
        await self.bot.wait_until_ready()

# BURASI ÇOK ÖNEMLİ: Setup fonksiyonu bot değişkenini main.py'den alır
async def setup(bot):
    await bot.add_cog(ZamanlanmisMesaj(bot))
