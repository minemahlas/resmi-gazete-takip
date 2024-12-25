import os
import requests
from bs4 import BeautifulSoup
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ParseMode

# Resmi Gazete URL'si
URL = "https://www.resmigazete.gov.tr/"

# Anahtar kelimeler
KEYWORDS = [
    "Basın İş Kanunu",
    "Yayın Hizmetleri Usul ve Esasları",
    "Resmi İlan ve Reklam",
    "Temiz Enerji ve Enerji",
    "İş Kanunu",
    "Anayasa Mahkemesi",
    "Radyo ve Televizyon Üst Kurulu",
    "Ticaret Kanunu",
]

# Telegram bot token ve chat ID (GitHub Secrets üzerinden alınacak)
BOT_TOKEN = os.getenv("BOT_TOKEN")

def extract_sentences_with_keywords(content, keywords):
    """İçeriği cümlelere ayırır ve anahtar kelimeleri içeren cümleleri döndürür."""
    sentences = re.split(r'(?<=[.!?]) +', content)  # Nokta, ünlem ve soru işaretinden sonra bölerek cümlelere ayırır
    matching_sentences = [
        sentence for sentence in sentences
        if any(keyword.lower() in sentence.lower() for keyword in keywords)
    ]
    return matching_sentences

def check_resmi_gazete():
    """Resmi Gazete içeriğini kontrol eder ve eşleşen cümleleri döndürür."""
    try:
        print("Resmi Gazete'den içerik çekiliyor...")
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # HTTP hata kontrolü
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text()  # HTML içeriğini düz metin olarak alır
        print("İçerik başarıyla çekildi.")
        
        # Anahtar kelimeleri içeren cümleleri bul
        matching_sentences = extract_sentences_with_keywords(content, KEYWORDS)
        return matching_sentences
    except requests.exceptions.RequestException as e:
        print(f"Bağlantı hatası: {e}")
        return []

def send_telegram_message(update: Update, context: CallbackContext, sentences):
    """Eşleşen cümleleri Telegram üzerinden gönderir."""
    if not sentences:
        update.message.reply_text("📄 <b>Resmi Gazete Güncellemesi</b>\n\nHiçbir eşleşen cümle bulunamadı.")
        return

    message = "📄 <b>Resmi Gazete Güncellemesi</b>\n\n"
    message += "\n".join([f"- {sentence}" for sentence in sentences])
    update.message.reply_text(message, parse_mode=ParseMode.HTML)

def start(update: Update, context: CallbackContext):
    """Bot başladığında çalışacak fonksiyon."""
    update.message.reply_text("Merhaba! Resmi Gazete'yi taramak için /scan komutunu kullanabilirsiniz.")

def scan(update: Update, context: CallbackContext):
    """/scan komutunu işleyen fonksiyon."""
    update.message.reply_text("Resmi Gazete taraması başlatılıyor... Lütfen bekleyin.")
    matching_sentences = check_resmi_gazete()
    send_telegram_message(update, context, matching_sentences)

def main():
    """Telegram botunun çalıştığı ana fonksiyon."""
    updater = Updater(BOT_TOKEN)

    # Komutlar
    updater.dispatcher.add_handler(CommandHandler("start", start))  # /start komutu
    updater.dispatcher.add_handler(CommandHandler("scan", scan))    # /scan komutu

    # Botu çalıştır
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
