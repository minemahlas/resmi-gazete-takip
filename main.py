import requests
from bs4 import BeautifulSoup
import re
import os

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
CHAT_ID = os.getenv("CHAT_ID")


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


def send_telegram_message(sentences):
    """Eşleşen cümleleri Telegram üzerinden gönderir."""
    if not sentences:
        print("Gönderilecek cümle bulunamadı.")
        return

    message = "📄 <b>Resmi Gazete Güncellemesi</b>\n\n"
    message += "\n".join([f"- {sentence}" for sentence in sentences])
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        print("Telegram mesajı gönderiliyor...")
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Telegram mesajı başarıyla gönderildi.")
    except requests.exceptions.RequestException as e:
        print(f"Telegram mesajı gönderiminde hata: {e}")


if __name__ == "__main__":
    matching_sentences = check_resmi_gazete()
    send_telegram_message(matching_sentences)
