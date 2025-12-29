# Bot Kurulum Notları

## ✅ Token Eklendikten Sonra Yapılması Gerekenler

### 1. Discord Developer Portal Ayarları

Bot'unuzun düzgün çalışması için şu ayarları yapmanız gerekiyor:

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin
2. Bot'unuzu seçin
3. **"Bot"** sekmesine gidin
4. **"Privileged Gateway Intents"** bölümünde şunları aktif edin:
   - ✅ **MESSAGE CONTENT INTENT** (Zorunlu - Mesaj içeriğini okumak için)
   - ✅ **SERVER MEMBERS INTENT** (İsteğe bağlı - Kullanıcı bilgileri için)

### 2. Bot'u Sunucuya Ekleme

Bot'u sunucunuza eklerken şu izinleri verin:

**Zorunlu İzinler:**
- ✅ Send Messages (Mesaj Gönderme)
- ✅ Manage Messages (Mesaj Yönetme) - Komutları kullanmak için
- ✅ Read Message History (Mesaj Geçmişini Okuma)
- ✅ Mention Everyone (@everyone yapabilmek için)

**Önerilen İzinler:**
- ✅ Embed Links (Embed mesajlar için)
- ✅ Read Messages/View Channels (Kanalları görme)

### 3. Bot'u Çalıştırma

```bash
# Sanal ortamı aktif edin (eğer kullanıyorsanız)
source botortami/bin/activate

# Gerekli paketleri yükleyin (eğer yüklemediyseniz)
pip install -r requirements.txt

# Bot'u çalıştırın
python main.py
```

### 4. Test Etme

Bot çalıştıktan sonra Discord'da test edin:

1. Bot'un çevrimiçi olduğunu kontrol edin
2. Bir kanalda `!ping` komutunu deneyin
3. Bir kanalda `!mesaj-baslat 14:30 Test mesajı` komutunu deneyin
4. Belirtilen saatte (14:30, 15:30, 16:30...) mesajın gönderildiğini kontrol edin
5. 3 dakika sonra mesajın otomatik silindiğini kontrol edin

## ⚠️ Önemli Notlar

- Bot'un @everyone mention yapabilmesi için "Mention Everyone" izni verilmiş olmalı
- Bot'un mesaj silme yetkisi olmalı (Manage Messages)
- Bot'un çalıştığı sürece zamanlanmış mesajlar otomatik gönderilir
- Bot'u kapatırsanız, açtığınızda zamanlanmış mesajlar devam eder (veritabanında saklanır)

## 🔧 Sorun Giderme

**Bot çalışmıyor:**
- Token'ın doğru olduğundan emin olun
- `.env` dosyasının doğru formatta olduğunu kontrol edin: `DISCORD_TOKEN=token_buraya`
- Tırnak işareti kullanmayın: `DISCORD_TOKEN="token"` ❌ → `DISCORD_TOKEN=token` ✅

**Mesaj gönderilmiyor:**
- Bot'un kanalda "Send Messages" izni olduğundan emin olun
- Bot'un @everyone mention yapma izni olduğundan emin olun
- Saat formatının doğru olduğundan emin olun (HH:MM)

**Mesaj silinmiyor:**
- Bot'un "Manage Messages" izni olduğundan emin olun
- Mesajın 3 dakikadan eski olmadığından emin olun


