import discord
from discord.ext import commands
import random

class Eglence(commands.Cog):
    """Eğlence komutları"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='zar', aliases=['dice'])
    async def zar(self, ctx, yuz: int = 6):
        """Zar atar (varsayılan 6 yüzlü)"""
        if yuz < 2:
            await ctx.send('Zar en az 2 yüzlü olmalı!')
            return
        if yuz > 100:
            await ctx.send('Zar en fazla 100 yüzlü olabilir!')
            return
        
        sonuc = random.randint(1, yuz)
        await ctx.send(f'🎲 Zar atıldı! Sonuç: **{sonuc}** (1-{yuz})')

    @commands.command(name='yazitura', aliases=['coin', 'para'])
    async def yazitura(self, ctx):
        """Yazı tura atar"""
        sonuc = random.choice(['Yazı', 'Tura'])
        await ctx.send(f'🪙 **{sonuc}**!')

    @commands.command(name='sec', aliases=['choose', 'karar'])
    async def sec(self, ctx, *secenekler):
        """Seçenekler arasından rastgele birini seçer"""
        if not secenekler:
            await ctx.send('Lütfen en az bir seçenek belirtin! Örnek: `!sec elma armut muz`')
            return
        
        secilen = random.choice(secenekler)
        await ctx.send(f'🎯 Seçilen: **{secilen}**')

    @commands.command(name='sayi', aliases=['random', 'rastgele'])
    async def sayi(self, ctx, min_sayi: int = 1, max_sayi: int = 100):
        """Belirtilen aralıkta rastgele bir sayı üretir"""
        if min_sayi > max_sayi:
            await ctx.send('Minimum sayı maksimum sayıdan büyük olamaz!')
            return
        
        sonuc = random.randint(min_sayi, max_sayi)
        await ctx.send(f'🔢 Rastgele sayı: **{sonuc}** ({min_sayi}-{max_sayi})')

async def setup(bot):
    await bot.add_cog(Eglence(bot))

