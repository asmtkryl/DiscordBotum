# Veritabanı Hakkında Bilgiler

## 📁 Veritabanı Dosyası

Bot, zamanlanmış mesajları **yerel bir SQLite veritabanı dosyasında** saklar:
- Dosya adı: `zamanlanmis_mesajlar.db`
- Konum: Bot klasörünün içinde
- Format: SQLite (hafif, taşınabilir)

## ✅ Önemli Bilgiler

### 1. Veriler Kalıcıdır
- ✅ Bot kapansa bile **veriler kaybolmaz**
- ✅ Bilgisayarınızı kapatıp açsanız bile **ayarlar korunur**
- ✅ Bot'u yeniden başlattığınızda **tüm zamanlanmış mesajlar devam eder**

### 2. Bot Çalışması Gereklidir
- ⚠️ Bot **çalıştığı sürece** mesajlar gönderilir
- ⚠️ Bot kapalıyken mesaj gönderilmez
- ✅ Bot'u tekrar açtığınızda, ayarlar korunmuş olur ve mesajlar gönderilmeye devam eder

### 3. Veritabanı Dosyası
- Dosya otomatik oluşturulur (ilk komut çalıştırıldığında)
- Dosyayı silebilirsiniz (tüm ayarlar silinir)
- Dosyayı yedekleyebilirsiniz (ayarları korumak için)
- Dosya `.gitignore`'da olduğu için Git'e commit edilmez

## 🔄 Nasıl Çalışır?

1. **Bot'u başlatın** → Veritabanı kontrol edilir
2. **Zamanlanmış mesaj oluşturun** → Veritabanına kaydedilir
3. **Bot çalışırken** → Her saat başında mesaj gönderilir
4. **Bot'u kapatın** → Veriler kaybolmaz, sadece mesaj gönderilmez
5. **Bot'u tekrar açın** → Ayarlar korunmuş, mesajlar devam eder

## 💡 Öneriler

- Bot'u sürekli çalıştırmak için bir VPS veya bulut sunucu kullanabilirsiniz
- Veya bilgisayarınızı açık tutabilirsiniz
- Veritabanı dosyasını düzenli olarak yedekleyebilirsiniz

## 🚀 Bulut Çözümü İsterseniz

Eğer bot'u sürekli çalıştırmak istiyorsanız:
- **Replit** (ücretsiz, sınırlı)
- **Heroku** (ücretsiz tier kaldırıldı)
- **Railway** (ücretsiz tier var)
- **VPS** (DigitalOcean, AWS, vb.)

Bu platformlarda bot'u 7/24 çalıştırabilirsiniz.


