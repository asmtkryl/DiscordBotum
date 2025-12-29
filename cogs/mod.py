import discord
from discord.ext import commands

class Mod(commands.Cog):
    """Moderasyon komutları"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='temizle', aliases=['clear', 'sil'])
    @commands.has_permissions(manage_messages=True)
    async def temizle(self, ctx, miktar: int = 5):
        """Belirtilen sayıda mesajı siler (varsayılan: 5)"""
        if miktar < 1 or miktar > 100:
            await ctx.send('Lütfen 1 ile 100 arasında bir sayı girin!')
            return
        
        try:
            deleted = await ctx.channel.purge(limit=miktar + 1)  # +1 komut mesajını da silmek için
            await ctx.send(f'✅ {len(deleted) - 1} mesaj silindi!', delete_after=3)
        except discord.Forbidden:
            await ctx.send('❌ Mesajları silme yetkim yok!')
        except Exception as e:
            await ctx.send(f'❌ Bir hata oluştu: {str(e)}')

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, sebep=None):
        """Bir kullanıcıyı sunucudan atar"""
        if member == ctx.author:
            await ctx.send('❌ Kendinizi atamazsınız!')
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('❌ Bu kullanıcıyı atma yetkiniz yok!')
            return
        
        try:
            await member.kick(reason=sebep)
            await ctx.send(f'✅ {member.mention} sunucudan atıldı. Sebep: {sebep or "Belirtilmedi"}')
        except discord.Forbidden:
            await ctx.send('❌ Bu kullanıcıyı atma yetkim yok!')
        except Exception as e:
            await ctx.send(f'❌ Bir hata oluştu: {str(e)}')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, sebep=None):
        """Bir kullanıcıyı sunucudan yasaklar"""
        if member == ctx.author:
            await ctx.send('❌ Kendinizi yasaklayamazsınız!')
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('❌ Bu kullanıcıyı yasaklama yetkiniz yok!')
            return
        
        try:
            await member.ban(reason=sebep)
            await ctx.send(f'✅ {member.mention} sunucudan yasaklandı. Sebep: {sebep or "Belirtilmedi"}')
        except discord.Forbidden:
            await ctx.send('❌ Bu kullanıcıyı yasaklama yetkim yok!')
        except Exception as e:
            await ctx.send(f'❌ Bir hata oluştu: {str(e)}')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, kullanici):
        """Yasaklı bir kullanıcının yasağını kaldırır"""
        banned_users = [entry async for entry in ctx.guild.bans()]
        
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == kullanici or str(user.id) == kullanici:
                try:
                    await ctx.guild.unban(user)
                    await ctx.send(f'✅ {user.mention} yasağı kaldırıldı!')
                    return
                except Exception as e:
                    await ctx.send(f'❌ Bir hata oluştu: {str(e)}')
                    return
        
        await ctx.send(f'❌ {kullanici} kullanıcısı yasaklılar listesinde bulunamadı!')

async def setup(bot):
    await bot.add_cog(Mod(bot))

