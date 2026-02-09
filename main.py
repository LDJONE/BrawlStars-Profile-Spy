import requests
import time
import os
from flask import Flask
from threading import Thread

# Загрузка настроек из переменных окружения Render
API_KEY = os.getenv("BS_API_KEY")
# Убираем решетку, если она случайно попала в переменную, и заменяем для URL
PLAYER_TAG = os.getenv("PLAYER_TAG", "JC2YRUJ8L").replace("#", "").strip()
URL_TAG = f"%23{PLAYER_TAG}"

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask('')

@app.route('/')
def home():
    return f"Бот следит за игроком {PLAYER_TAG}!"

def run_web():
    # Render требует порт 8080 или динамический из переменной PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def check_loop():
    last_battle_time = None
    print(f"--- ЗАПУСК МОНИТОРИНГА: {PLAYER_TAG} ---")
    
    while True:
        try:
            url = f"https://api.brawlstars.com/v1/players/{URL_TAG}/battlelog"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Логируем статус для отладки
            print(f"LOG: Статус запроса к BS API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if items:
                    current_battle_time = items[0].get('battleTime')
                    
                    # Если это первый запуск, просто запоминаем время
                    if last_battle_time is None:
                        last_battle_time = current_battle_time
                        print(f"LOG: Начальное время боя зафиксировано: {last_battle_time}")
                    
                    # Если время изменилось — значит, прошел новый бой
                    elif current_battle_time != last_battle_time:
                        print("!!! ОБНАРУЖЕН НОВЫЙ БОЙ !!!")
                        last_battle_time = current_battle_time
                        
                        # Отправка уведомления в Telegram
                        msg = f"🎮 Игрок {PLAYER_TAG} закончил матч! Он онлайн."
                        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
                        requests.post(tg_url, json={"chat_id": CHAT_ID, "text": msg})
                else:
                    print("LOG: Battle log пуст.")
            
            elif response.status_code == 403:
                print("ERROR: Ошибка 403 (Forbidden). Проверь IP-адрес в ключе API Brawl Stars!")
            else:
                print(f"ERROR: API вернул {response.status_code}: {response.text}")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
        
        # Проверка каждую минуту (60 сек)
        time.sleep(60)

if __name__ == "__main__":
    # Запускаем мониторинг в отдельном потоке
    monitor_thread = Thread(target=check_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Запускаем Flask для Render
    run_web()
