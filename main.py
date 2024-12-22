import requests
import time

# Resmî Gazete URL
URL = "https://www.resmigazete.gov.tr"

def check_resmi_gazete():
    """
    Resmî Gazete sayfasına bağlanır ve içeriği kontrol eder.
    """
    for attempt in range(3):  # 3 kez dene
        try:
            print(f"Attempt {attempt + 1}: Connecting to {URL}...")
            response = requests.get(URL, timeout=20)  # 20 saniye timeout
            response.raise_for_status()  # HTTP hatalarını yakalar
            print("Connection successful!")
            return response.text  # İçeriği döndür
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if attempt < 2:  # Son deneme değilse bekle
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All attempts failed. Exiting.")
                raise e

if __name__ == "__main__":
    try:
        content = check_resmi_gazete()
        print("First 100 characters of the page:")
        print(content[:100])  # Sayfanın ilk 100 karakterini yazdır
    except Exception as e:
        print(f"Failed to fetch the page: {e}")
