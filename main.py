import requests
import time
import os
from flask import Flask
from threading import Thread

# Настройки из переменных окружения (безопаснее)
API_KEY = os.getenv("BS_API_KEY")
PLAYER_TAG = "%23JC2YRUJ8L"
TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

last_battle_time = None

def check_loop():
    global last_battle_time
    while True:
        try:
            url = f"https://api.brawlstars.com/v1/players/{PLAYER_TAG}/battlelog"
            headers = {"Authorization": f"Bearer {API_KEY}"}
            res = requests.get(url, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                current_time = data['items'][0]['battleTime']
                
                if last_battle_time and current_time != last_battle_time:
                    msg = "🎮 Игрок завершил матч! Он сейчас в сети."
                    requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}")
                
                last_battle_time = current_time
        except Exception as e:
            print(f"Ошибка: {e}")
        
        time.sleep(120) # Проверка каждые 2 минуты

# Запуск веб-сервера и цикла проверки одновременно
if __name__ == "__main__":
    t = Thread(target=check_loop)
    t.start()
    run_web()
