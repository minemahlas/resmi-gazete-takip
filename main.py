import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Resmi Gazete URL'si
URL = "https://www.resmigazete.gov.tr/"

# Anahtar kelimeler
KEYWORDS = [
    "Basın İş Kanunu",
    "Yayın Hizmetleri Usul ve Esasları",
    "Resmi İlan ve Reklam",
    "İş Kanunu",
    "Radyo ve Televizyon Üst Kurulu",
    "Ticaret Kanunu",
]

# Proxy ve headers
PROXY = {"http": "http://proxy_address:port", "https": "http://proxy_address:port"}  # Gerekirse proxy bilgilerini girin
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

def check_resmi_gazete():
    try:
        response = requests.get(URL, headers=HEADERS, proxies=PROXY, timeout=10)
        response.raise_for_status()  # HTTP hata kodları için kontrol
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.text

        # Anahtar kelimeleri kontrol et
        matches = [keyword for keyword in KEYWORDS if keyword in content]
        return matches
    except requests.exceptions.RequestException as e:
        print(f"Bağlantı hatası: {e}")
        return []

def send_email(matches):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    if matches:
        subject = "Resmi Gazete'de Yeni Güncelleme"
        body = f"Resmi Gazete'de şu anahtar kelimeler bulundu: {', '.join(matches)}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print("E-posta başarıyla gönderildi.")
        except Exception as e:
            print(f"E-posta gönderiminde hata: {e}")

if __name__ == "__main__":
    matches = check_resmi_gazete()
    if matches:
        send_email(matches)
    else:
        print("Anahtar kelime bulunamadı.")
