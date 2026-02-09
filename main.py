import requests
import time
import os
from flask import Flask
from threading import Thread

# Загрузка настроек
API_KEY = os.getenv("BS_API_KEY")
# Теперь используем твой новый ID профиля
PLAYER_TAG = os.getenv("PLAYER_TAG", "PRGQP2PLQ").replace("#", "").strip().upper()
URL_TAG = f"%23{PLAYER_TAG}"

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask('')

@app.route('/')
def home():
    return f"Бот следит за твоим профилем: {PLAYER_TAG}"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def check_loop():
    last_battle_time = None
    print(f"--- МОНИТОРИНГ ТВОЕГО ПРОФИЛЯ: {PLAYER_TAG} ---")
    
    while True:
        try:
            url = f"https://api.brawlstars.com/v1/players/{URL_TAG}/battlelog"
            headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if items:
                    current_battle_time = items[0].get('battleTime')
                    
                    if last_battle_time is None:
                        last_battle_time = current_battle_time
                        print(f"LOG: Текущий бой в памяти: {last_battle_time}. Жду новую катку...")
                    
                    elif current_battle_time != last_battle_time:
                        print("!!! ТЫ ЗАКОНЧИЛ БОЙ !!! Отправляю пуш...")
                        last_battle_time = current_battle_time
                        
                        msg = f"🎮 Илья, зафиксирован новый бой в твоем профиле {PLAYER_TAG}! Ты онлайн."
                        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
                        requests.post(tg_url, json={"chat_id": CHAT_ID, "text": msg})
                else:
                    print("LOG: История боев пуста.")
            else:
                print(f"ERROR: BS API вернул {response.status_code}. Проверь IP в ключе!")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
        
        time.sleep(60) # Проверка раз в минуту

if __name__ == "__main__":
    monitor_thread = Thread(target=check_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    run_web()

