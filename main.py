import gspread, cloudscraper, re, os, json, time
from oauth2client.service_account import ServiceAccountCredentials

def run():
    creds = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    client = gspread.authorize(ServiceAccountCredentials.from_json_dict(creds, scope))
    sheet = client.open_by_key(os.environ['SHEET_ID']).sheet1
    
    urls = sheet.col_values(1)
    scraper = cloudscraper.create_scraper()

    for i, url in enumerate(urls):
        if "prodoctorov.ru" in url:
            res = scraper.get(url)
            match = re.search(r'"reviewCount":\s*(\d+)', res.text)
            if match:
                sheet.update_cell(i + 1, 2, match.group(1))
            time.sleep(3)

if __name__ == "__main__":
    run()