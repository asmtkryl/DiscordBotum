# Discord Botu

Modern ve güvenli bir Discord botu projesi. Zamanlanmış mesaj sistemi ile saatte bir otomatik @everyone çağrısı yapabilir.

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### 2. Sanal Ortam Oluşturma (Önerilen)

```bash
python3 -m venv botortami
source botortami/bin/activate  # macOS/Linux için
# veya
botortami\Scripts\activate  # Windows için
```

### 3. Paketleri Yükleme

```bash
pip install -r requirements.txt
```

### 4. Bot Token'ını Ayarlama

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin
2. Yeni bir uygulama oluşturun veya mevcut uygulamanızı seçin
3. "Bot" sekmesine gidin ve bir bot oluşturun
4. Bot token'ınızı kopyalayın
5. Proje klasöründe `.env` adında bir dosya oluşturun
6. `.env` dosyasına şunu ekleyin:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```
7. `your_bot_token_here` kısmını kendi bot token'ınızla değiştirin

### 5. Botu Çalıştırma

```bash
python main.py
```

## 📝 Mevcut Komutlar

### Genel Komutlar
- `!merhaba` veya `!selam` veya `!hi` - Bot size merhaba der
- `!ping` - Botun gecikme süresini gösterir
- `!bilgi` - Bot hakkında bilgi verir

### Eğlence Komutları
- `!zar [yüz]` - Zar atar (varsayılan 6 yüzlü)
- `!yazitura` - Yazı tura atar
- `!sec <seçenek1> <seçenek2> ...` - Seçenekler arasından rastgele birini seçer
- `!sayi [min] [max]` - Belirtilen aralıkta rastgele sayı üretir

### Moderasyon Komutları
- `!temizle [miktar]` - Belirtilen sayıda mesajı siler (Mesaj Yönetme yetkisi gerekir)
- `!kick <kullanıcı> [sebep]` - Kullanıcıyı sunucudan atar (Üyeleri Atma yetkisi gerekir)
- `!ban <kullanıcı> [sebep]` - Kullanıcıyı sunucudan yasaklar (Üyeleri Yasaklama yetkisi gerekir)
- `!unban <kullanıcı>` - Yasaklı kullanıcının yasağını kaldırır (Üyeleri Yasaklama yetkisi gerekir)

### Zamanlanmış Mesaj Komutları ⏰
- `!mesaj-baslat <saat> <mesaj>` - Belirtilen odada zamanlanmış mesajı başlatır (Mesaj Yönetme yetkisi gerekir)
  - Örnek: `!mesaj-baslat 14:30 Etkinlik başlıyor!`
  - Mesaj her saat başında (belirtilen dakikada) @everyone ile gönderilir ve 3 dakika sonra otomatik silinir
- `!mesaj-durdur` - Bu odadaki zamanlanmış mesajı durdurur (Mesaj Yönetme yetkisi gerekir)
- `!mesaj-listele` - Sunucudaki tüm zamanlanmış mesajları listeler (Mesaj Yönetme yetkisi gerekir)
- `!mesaj-bilgi` - Bu odadaki zamanlanmış mesaj hakkında bilgi verir (Mesaj Yönetme yetkisi gerekir)
- `!mesaj-test` - Zamanlanmış mesaj sistemini test eder (hemen bir mesaj gönderir) (Mesaj Yönetme yetkisi gerekir)
- `!mesaj-sil [oda_id]` - Zamanlanmış mesajı tamamen siler (Mesaj Yönetme yetkisi gerekir)
  - Oda ID belirtilmezse mevcut odadaki mesaj silinir

**Önemli:** Bot çalıştığı sürece mesajlar gönderilir. Bot kapansa bile ayarlar kaybolmaz (veritabanında saklanır). Detaylar için `VERITABANI_BILGI.md` dosyasına bakın.

## 🔧 Özelleştirme

Botu özelleştirmek için `main.py` dosyasındaki komutları düzenleyebilir veya yeni komutlar ekleyebilirsiniz.

### Yeni Komut Ekleme

**main.py'ye direkt ekleme:**
```python
@bot.command(name='komut_adi')
async def komut_fonksiyonu(ctx):
    """Komut açıklaması"""
    await ctx.send('Komut çalıştı!')
```

**Cog olarak ekleme (Önerilen):**
`cogs/` klasöründe yeni bir Python dosyası oluşturun ve şu şablonu kullanın:

```python
import discord
from discord.ext import commands

class YeniCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='komut_adi')
    async def komut_fonksiyonu(self, ctx):
        """Komut açıklaması"""
        await ctx.send('Komut çalıştı!')

async def setup(bot):
    await bot.add_cog(YeniCog(bot))
```

Sonra `main.py` dosyasındaki `on_ready` event'ine şunu ekleyin:
```python
await bot.load_extension('cogs.yeni_cog_dosya_adi')
```

## ⚠️ Güvenlik

- **ASLA** `.env` dosyasını Git'e commit etmeyin
- Bot token'ınızı kimseyle paylaşmayın
- Token'ınızı sızdırırsanız, Discord Developer Portal'dan yeni bir token oluşturun

## 📚 Kaynaklar

- [Discord.py Dokümantasyonu](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)

## 🤝 Katkıda Bulunma

Bu projeyi geliştirmek için önerilerinizi paylaşabilirsiniz!

