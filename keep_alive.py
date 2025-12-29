from flask import Flask
from threading import Thread

# Flask uygulaması oluşturuluyor
app = Flask('')

@app.route('/')
def home():
    # Render'ın 'yaşıyor mu?' kontrolüne cevap verecek mesaj
    return "Bot Aktif ve Calisiyor!"

def run():
    # Sunucuyu 8080 portunda başlatıyoruz
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Web sunucusunu botla aynı anda çalışması için bir thread (iş parçacığı) olarak başlatıyoruz
    t = Thread(target=run)
    t.start()
