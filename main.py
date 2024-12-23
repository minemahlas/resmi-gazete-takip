import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import re
from datetime import datetime
import time

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

# Headers (isteğe bağlı düzenleyin)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

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
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()  # HTTP hata kontrolü
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text()  # HTML içeriğini düz metin olarak alır
        print("İçerik başarıyla çekildi.")
        
        # Anahtar kelimeleri içeren cümleleri bul
        matching_sentences = extract_sentences_with_keywords(content, KEYWORDS)
        print(f"Bulunan cümleler: {matching_sentences}")
        return matching_sentences
    except requests.exceptions.RequestException as e:
        print(f"Bağlantı hatası: {e}")
        return []

def send_email(sentences):
    """Eşleşen cümleleri e-posta olarak gönderir."""
    sender_email = os.getenv("EMAIL_USER")  # Gönderici e-posta adresi
    sender_password = os.getenv("EMAIL_PASS")  # Gönderici e-posta şifresi
    receiver_email = os.getenv("RECEIVER_EMAIL")  # Alıcı e-posta adresi

    if not sender_email or not sender_password or not receiver_email:
        print("E-posta bilgileri eksik! Lütfen ortam değişkenlerini kontrol edin.")
        return

    if sentences:
        subject = "Resmi Gazete Güncellemesi"
        body = "Resmi Gazete'de anahtar kelimeler içeren şu cümleler bulundu:\n\n" + "\n".join(sentences)

        # E-posta mesajını oluştur
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            print("SMTP sunucusuna bağlanılıyor...")
            server = smtplib.SMTP("smtp.office365.com", 587)
            server.starttls()
            print("Sunucuya giriş yapılıyor...")
            server.login(sender_email, sender_password)
            print("E-posta gönderiliyor...")
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print("E-posta başarıyla gönderildi.")
        except Exception as e:
            print(f"E-posta gönderiminde hata: {e}")
    else:
        print("Gönderilecek cümle bulunamadığı için e-posta gönderilmedi.")

if __name__ == "__main__":
    matching_sentences = check_resmi_gazete()
    send_email(matching_sentences)
