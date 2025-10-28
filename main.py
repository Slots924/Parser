import os
from datetime import datetime
from openpyxl import Workbook

# ---------------------------
# 🔧 НАЛАШТУВАННЯ
# ---------------------------
UA_INDEX = 3        # індекс поля з User Agent (рахується з 1)
COOKIE_INDEX = 5    # індекс поля з cookies (рахується з 1)
TAB_VALUE = "https://www.facebook.com/"  # значення для поля "tab"
PROXY_TYPE = "noproxy"                   # значення для поля "proxytype"

# 🧩 Сюди встав свої дані (кожен профіль окремим рядком)
data = """


oqvrrqrb@tacoblastmail.com. :: EAABsbCS1iHgBPipkN6vXSpwwEZC50nYkGgugKqYLkffsZCX7kqp04bYypiwCjFPpm5yIW0A4oPZBzSaksbf9zNy1cwuzbENvkYcdVSDVBlRkXbuesGNIiYKxhZC5PPS5v3BymeQsghUxC2OqFjMZCSVOpnXrawIueY6FpO1ZCtYJtzLAYyzzZAB3VpDcISMPMvOygZDZD :: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 ::  :: [{"domain":".facebook.com","expirationDate": 1793256457999,"httpOnly": true,"name":"datr","path":"/","secure": true,"value":"CZTTaKboGz1UuKRcWGFxRVhl"},{"domain":".facebook.com","expirationDate": 1793256484999,"httpOnly": true,"name":"sb","path":"/","secure": true,"value":"C5TTaCNaJgm_GFluUOpm_sb9"},{"domain":".facebook.com","expirationDate": 1759301953999,"httpOnly": false,"name":"wd","path":"/","secure": true,"value":"992x482"},{"domain":".facebook.com","expirationDate": 1790233049999,"httpOnly": false,"name":"c_user","path":"/","secure": true,"value":"61581018646177"},{"domain":".facebook.com","expirationDate": 1793256484999,"httpOnly": true,"name":"ps_l","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1793256484999,"httpOnly": true,"name":"ps_n","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1766473049999,"httpOnly": true,"name":"fr","path":"/","secure": true,"value":"1CXG3Uu4bcBPeTqMY.AWelBus1ZbWQhOHk_amopoiLFUsyo5Ir92cOIT0eEqHvGGQU3Qw.Bo05ZZ..AAA.0.0.Bo05ZZ.AWfpvpZnyfcCnZaUZa-96axCYmI"},{"domain":".facebook.com","expirationDate": 1790233049999,"httpOnly": true,"name":"xs","path":"/","secure": true,"value":"46%3ALRfHb2-I2fd3Cw%3A2%3A1758696483%3A-1%3A-1%3A%3AAcXEEvfxIc5-pt0F1B0bGgJdP5gieAMa_RcweyGPvg"},{"domain":".facebook.com","expirationDate": -62135596800999,"httpOnly": false,"name":"presence","path":"/","secure": true,"value":"C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1758697154210%2C%22v%22%3A1%7D"}] :: m@ixR247XWD :: oqvrrqrb@tacoblastmail.com.;m@ixR247XWD;upbxbduqY!3856;4.8.2001;61581018646177; ;https://2fa.fb.rip/; LIMIT 50; GEO Ukraine;БМ1 EAAGNO4a7r2wBPmZCI1fdZAT1L0CEuZC2xf1ZCJeZCMa7EOXZAqmwY208hbmU10tKqsj82G50dbwCrOg0aKIeZAZAcCP4yZAPIMTgUURONV0t02rJOdM5FZCjQCUr1jSrYmtjZCXnRMXJvbJZCEqZCvPhrLqd1QMQ14p0vbfgChahbSybbfVpP9yZAZCCgNqxquWpOpicyQungZDZD;1432102211185146;БМ2 EAAGNO4a7r2wBPpMxZACYoDK7ZC4W3cK6JlnU1SkHpCGfywzPaDuNNdUtfxukE2hblM9Yuot8YjJQCDQkWmzalzD7bQIcbNnrdOcudsMrL9m7GCmod8krrVsGZA81QETEZASGsbNYQ689eoFVHiVH4o6akDtGTl1yWKLJ6ZAr8ykjRNZAN2oDdl4uTDLunucddoZAQZDZD;1856424698635504; FP; AVA https://i.postimg.cc/Vk9Ctgrw/0589-3-Pm-Knb-Uc-Sy-Y.jpg; DOC ; 51
pnfplgwy@vargosmail.com. :: EAABsbCS1iHgBPurQAwaFEx33mqHbJI1DVqMJEeVvwAKzZAoCFZAzGeqoIEkAsPJ90qlZAUOrb0YgmvsvepW8LRAZAZBi7ChhxegXHYdyZALsMu43nOucsuEFdHI7aVa3bMLoL6eyMnAro2480d47CO5HLyczfzDaaWhIoEw7EAYeTfIxVcCEdprJgF20XWQAZDZD :: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ::  :: [{"domain":".facebook.com","expirationDate": 1793268678999,"httpOnly": true,"name":"datr","path":"/","secure": true,"value":"xsPTaP8q9t9wRKmPIEHOIy8J"},{"domain":".facebook.com","expirationDate": 1793268707999,"httpOnly": true,"name":"sb","path":"/","secure": true,"value":"ycPTaAwlnB08xtYSv8Tv3MdL"},{"domain":".facebook.com","expirationDate": 1759314426999,"httpOnly": false,"name":"wd","path":"/","secure": true,"value":"992x482"},{"domain":".facebook.com","expirationDate": 1790245438999,"httpOnly": false,"name":"c_user","path":"/","secure": true,"value":"61581335131403"},{"domain":".facebook.com","expirationDate": 1793268708999,"httpOnly": true,"name":"ps_l","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1793268708999,"httpOnly": true,"name":"ps_n","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1766485438999,"httpOnly": true,"name":"fr","path":"/","secure": true,"value":"1YtPyy18EkD24iNe3.AWfh0dihotXyTJKBOZKBenMuHFanyfdYSZw65i5cCRxDwwwT0f8.Bo08a-..AAA.0.0.Bo08a-.AWdFL-MSvoaixAuVQN6qaA3jdg0"},{"domain":".facebook.com","expirationDate": 1790245438999,"httpOnly": true,"name":"xs","path":"/","secure": true,"value":"43%3AsfGsL3cOLV84cA%3A2%3A1758708704%3A-1%3A-1%3A%3AAcWi-K-qlg4-W4_Y15lPUXlNGBRBQQcjV7u8O5aX0A"},{"domain":".facebook.com","expirationDate": -62135596800999,"httpOnly": false,"name":"presence","path":"/","secure": true,"value":"C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1758709627720%2C%22v%22%3A1%7D"}] :: 6C%@2ptR :: pnfplgwy@vargosmail.com.;6C%@2ptR;dzfonmohY!5713;22.2.1983;61581335131403; ;https://2fa.fb.rip/; LIMIT 50; GEO Ukraine;БМ1 EAAGNO4a7r2wBPilU5epKIqiNZCjkRACj5zV2V8Gd6bBtzv5A0n8Jp0XZCyN0ofHHX9V31Y3VQuvAhfURLFfSZCwLbf17ZAQ95oXGZAD8MIY6D9Y1pYh5YUfQygkVbOqC6R9CCTpGWDTi8zLoFN3RDIcdyK88EML4dUyjLXQ0QhSZA9itNTi6iJhc9ThKxrCAZDZD;1876530403227159;БМ2 EAAGNO4a7r2wBPv6zSyaXJgIMqmW59xMTPdqkL4FS0tFeU7ZAurU9POEBWPXLgd6NIoLTHHf3Qk10jqfZBghkNlYtgWjhh9xwt2U0Boa8WzEi5Lc1gRbNFuxFZAYJZAZAnfabAkTIVqYRRvY5ZA5R2Kiu0mhEFNat4nZCSnM5QPTMAv6RgFF5CAuWlomoztUeQZDZD;2016418185838286; FP; AVA https://i.postimg.cc/yYnbhMJN/3953-2-Fn-YZRCs-PPM.jpg; DOC ; 24
xleycgks@vargosmail.com. :: EAABsbCS1iHgBPmPEHRReDAf7PboSFkXo2wMVzRd9ZC4WQt5xfwUhp8uJLkjKZCmgKaqDZC8ZCSrZBFoDZAj5gQXAtUW6I5nfH2ZCZAIm1mNOWPZBKVxod9JINBKkU9LPvBFPz3eevPkdfy3euL6NY8dFXEokziKcoURA38OpYha99CBkHpAZCSzOFCfMh4LTswRgZDZD :: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ::  :: [{"domain":".facebook.com","expirationDate": 1793276258999,"httpOnly": true,"name":"datr","path":"/","secure": true,"value":"Y-HTaOlBtxwoaH1cltPG4QgP"},{"domain":".facebook.com","expirationDate": 1793276288999,"httpOnly": true,"name":"sb","path":"/","secure": true,"value":"ZeHTaNTdwlOkQf-gAoDyIoaz"},{"domain":".facebook.com","expirationDate": 1759321773999,"httpOnly": false,"name":"wd","path":"/","secure": true,"value":"992x482"},{"domain":".facebook.com","expirationDate": 1790252982999,"httpOnly": false,"name":"c_user","path":"/","secure": true,"value":"61581281104553"},{"domain":".facebook.com","expirationDate": 1793276910999,"httpOnly": true,"name":"ps_l","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1793276910999,"httpOnly": true,"name":"ps_n","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": -62135596800999,"httpOnly": false,"name":"presence","path":"/","secure": true,"value":"C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1758716980394%2C%22v%22%3A1%7D"},{"domain":".facebook.com","expirationDate": 1766492982999,"httpOnly": true,"name":"fr","path":"/","secure": true,"value":"1XOp3r1UFM5Kkmni5.AWcFApbGh2SFM95GRyYUt2Bo40KQrfvz91YL7i6lQsIq6AxhSnw.Bo0-Q2..AAA.0.0.Bo0-Q2.AWcnOXfy0Qq6AP_SsmwBujcbYj0"},{"domain":".facebook.com","expirationDate": 1790252982999,"httpOnly": true,"name":"xs","path":"/","secure": true,"value":"16%3A1o2JCEACDDWmhw%3A2%3A1758716286%3A-1%3A-1%3A%3AAcV-xc6jG3Q-Wg265vYFvbVZx8sITtalASE9ZhL3tA"}] :: Yj@9H2%b6us3 :: xleycgks@vargosmail.com.;Yj@9H2%b6us3;gseuuihlX!9868;6.7.1983;61581281104553; ;https://2fa.fb.rip/; LIMIT 50; GEO Ukraine;БМ1 EAAGNO4a7r2wBPl3wCrinvyTAr2cMSEEONFZAgdpVAZCv9lczuxuZBOIHNPsZAkGd4iRWX7AHU4OcEkoulRDgmKLP3x1nZB0F3HvkKFynl4feYtmbdF2LGLHcsu9BnVjUWXTZBnbV8aww2jAazZCb125lfrAdZBPGzBJdcoovuGgCpKsImkClZBDAC2fPmd52BTQZDZD;1485877542662486;БМ2 EAAGNO4a7r2wBPrJqZA4ORJX4XM0RIwuMKEQFbM1AUcbs4BxaxHa8SmDByL7YJ2J9ZBNVtq25wDhXeJdtKQJYW7pTZCJ1s2cPTtaAgaFNwUjSAziM8b1oVT1sLMLfYjaoNO2ZA71IgrZARZA7lRVvHXDZBkbBMFFcbC90drMDyZCCjkHGWNZBZBhFJrwZCUQOcgQZBQZDZD;670747822758018; FP; AVA https://i.postimg.cc/WbP7DXXb/0542-s-YEhc-EJDb2o.jpg; DOC ; 53
yjcwzkjp@tacoblastmail.com. :: EAABsbCS1iHgBPpqtClVDchJGZCVvZB0osQQZANhGk50RHvP3iYAc4rfXkhKpD1RwJIaY2taWGlfWERU4BIe0WSZAnSB00IlhNIAQ9DPR1Jpth9UpVNPDqrr1bKgc3MrMoN3WInPVdnO8WM7cYRzCM9NYIVpYIdsLzn4KrAsjMomU0eR97KBeJeUXwRZA0LkrUZCQZDZD :: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ::  :: [{"domain":".facebook.com","expirationDate": 1793276114999,"httpOnly": true,"name":"datr","path":"/","secure": true,"value":"0-DTaILMq5Rgb_Bo6-b0zY4H"},{"domain":".facebook.com","expirationDate": 1793276143999,"httpOnly": true,"name":"sb","path":"/","secure": true,"value":"1eDTaMjCdZm_g-f9wr1V1sBR"},{"domain":".facebook.com","expirationDate": 1759321757999,"httpOnly": false,"name":"wd","path":"/","secure": true,"value":"992x482"},{"domain":".facebook.com","expirationDate": 1790252461999,"httpOnly": false,"name":"c_user","path":"/","secure": true,"value":"61581438566244"},{"domain":".facebook.com","expirationDate": 1766492461999,"httpOnly": true,"name":"fr","path":"/","secure": true,"value":"1E0uRkfB4UpEE7eiF.AWdHlPVg51Ieft-r850XLTpRLqO0c62Qa6DQGD6n3irLgO60Ucc.Bo0-Iu..AAA.0.0.Bo0-Iu.AWcuUGu33gpYjurCZkgDkFO0UTw"},{"domain":".facebook.com","expirationDate": 1790252461999,"httpOnly": true,"name":"xs","path":"/","secure": true,"value":"4%3AsNwJtZ_o1M36xA%3A2%3A1758716142%3A-1%3A-1%3A%3AAcW5XJ6MBmzBTXmz3EuUjC0yOMjFRNw5G6G1ds4wQQ"},{"domain":".facebook.com","expirationDate": 1793276809999,"httpOnly": true,"name":"ps_l","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": 1793276809999,"httpOnly": true,"name":"ps_n","path":"/","secure": true,"value":"1"},{"domain":".facebook.com","expirationDate": -62135596800999,"httpOnly": false,"name":"presence","path":"/","secure": true,"value":"C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1758716958104%2C%22v%22%3A1%7D"}] :: @8Jns%T2ftE7 :: yjcwzkjp@tacoblastmail.com.;@8Jns%T2ftE7;pbycakhjY!2657;4.8.2001;61581438566244; ;https://2fa.fb.rip/; LIMIT 50; GEO Ukraine;БМ1 EAAGNO4a7r2wBPm21QQ3tToMs4TuySUF2ZAgzEIYcAy6G05ntq1eLC18IZBmKeCQWCHTPpE5lhNcABS5vBzyqPZAYs09RZAK41HXFZBvIuth8sKtZCNvwoiKYNtSSuk8sZAivypQB0ZBNwgK5IZBtvZCwNZBFEXqBZAVxNaurJboeK39ZApKW1okzAhERaCaUtOxifvIUeWgZDZD;1863131267606588;БМ2 EAAGNO4a7r2wBPpL6IL8LFNEqi7vxGMO5gaCzaRYqvCittazwk1Ex8FaBhFQITHbJccs4qygCG2x3CHs8jMR5PdfYdZChgBmrnKhu7NZBJwpMxKZCkZAYUluJp6qnHASQDf2OafdXLcX6lCFdHOcGM4p4CxbzELeETHPjz9JL8ulzmqkwXZA8jqHZCz5ZCLhwWKNRwZDZD;1521395998898515; FP; AVA https://i.postimg.cc/FK2LMH6g/0167-y8w2k-IMREIM.jpg; DOC ; 25

"""

# ---------------------------
# 🔍 ПАРСИНГ
# ---------------------------
SEP = " :: "
rows = []

for line_no, line in enumerate(data.splitlines(), start=1):
    line = line.strip()
    if not line:
        continue

    parts = [p.strip() for p in line.split(SEP)]

    # безпечне взяття поля (індекс рахується з 1)
    def get_field(index_1based: int) -> str:
        i = index_1based - 1
        return parts[i] if 0 <= i < len(parts) else ""

    ua = get_field(UA_INDEX)
    cookie = get_field(COOKIE_INDEX)

    # remark — усе, що йде після COOKIE_INDEX
    remark = f" {SEP} ".join(parts[COOKIE_INDEX:]).strip() if COOKIE_INDEX < len(parts) else ""

    # заповнюємо лише ті поля, які маємо, інші залишаємо порожніми
    row = {
        "name": "",
        "remark": remark,
        "tab": TAB_VALUE,
        "platform": "",
        "username": "",
        "password": "",
        "fakey": "",
        "cookie": cookie,
        "proxytype": PROXY_TYPE,
        "ipchecker": "",
        "proxy": "",
        "proxyurl": "",
        "proxyid": "",
        "ip": "",
        "countrycode": "",
        "regioncode": "",
        "citycode": "",
        "ua": ua,
        "resolution": ""
    }

    rows.append(row)

# ---------------------------
# 💾 СТВОРЕННЯ EXCEL-ФАЙЛУ
# ---------------------------
wb = Workbook()
ws = wb.active
ws.title = "Parsed Data"

# порядок колонок
headers = [
    "name", "remark", "tab", "platform", "username", "password", "fakey",
    "cookie", "proxytype", "ipchecker", "proxy", "proxyurl", "proxyid",
    "ip", "countrycode", "regioncode", "citycode", "ua", "resolution"
]
ws.append(headers)

# додавання рядків у потрібному порядку
for r in rows:
    ws.append([r[h] for h in headers])

# ---------------------------
# 📁 СТВОРЕННЯ ПАПКИ ТА ЗБЕРЕЖЕННЯ
# ---------------------------
output_dir = "resolt"
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_filename = os.path.join(output_dir, f"parsed_data_{timestamp}.xlsx")

wb.save(output_filename)
print(f"✅ Файл створено: {os.path.abspath(output_filename)}")