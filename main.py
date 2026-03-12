import gspread
import cloudscraper
import re
import os
import json
import time
from google.oauth2.service_account import Credentials

def run():
    # Настройка прав доступа
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Загрузка ключей из секретов GitHub
    creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = Credentials.from_service_account_info(creds_json, scopes=scope)
    
    # Авторизация
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_key(os.environ['SHEET_ID']).sheet1
    except Exception as e:
        print(f"Ошибка доступа к таблице: {e}")
        return

    urls = sheet.col_values(1)
    scraper = cloudscraper.create_scraper()

    for i, url in enumerate(urls):
        if url and "prodoctorov.ru" in url:
            print(f"Парсим: {url}")
            try:
                res = scraper.get(url)
                # Ищем число отзывов
                match = re.search(r'"reviewCount":\s*"?(\d+)"?', res.text)
                if match:
                    count = match.group(1)
                    sheet.update_cell(i + 1, 2, count)
                    print(f"Успех: {count} отзывов")
                else:
                    print("Число отзывов на странице не найдено")
            except Exception as e:
                print(f"Ошибка при запросе к сайту: {e}")
            
            time.sleep(5) # Пауза, чтобы не забанили

if __name__ == "__main__":
    run()
