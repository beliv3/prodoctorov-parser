import gspread
import cloudscraper
import re
import os
import json
import time
import ssl
from google.oauth2.service_account import Credentials

# Принудительная настройка SSL для обхода блокировок
ssl._create_default_https_context = ssl._create_unverified_context

def run():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = Credentials.from_service_account_info(creds_json, scopes=scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_key(os.environ['SHEET_ID']).sheet1
    except Exception as e:
        print(f"Ошибка таблицы: {e}")
        return

    urls = sheet.col_values(1)
    
    # Создаем скрейпер, имитирующий реальный браузер более детально
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    for i, url in enumerate(urls):
        if url and "prodoctorov.ru" in url:
            print(f"Попытка парсинга: {url}")
            try:
                # Добавляем таймаут и заголовки вручную
                res = scraper.get(url, timeout=20)
                
                if res.status_code == 200:
                    # Ищем число отзывов (разные варианты верстки)
                    match = re.search(r'"reviewCount":\s*"?(\d+)"?', res.text)
                    if not match:
                        match = re.search(r'(\d+)\s+отзыв', res.text)
                    
                    if match:
                        count = match.group(1)
                        sheet.update_acell(f'B{i + 1}', count)
                        print(f"Успех! Найдено отзывов: {count}")
                    else:
                        print("Ошибка: Число не найдено в коде страницы.")
                else:
                    print(f"Сайт ответил кодом: {res.status_code}")
                    
            except Exception as e:
                print(f"Критическая ошибка SSL/Сети: {e}")
            
            time.sleep(10) # Увеличиваем паузу для безопасности

if __name__ == "__main__":
    run()
