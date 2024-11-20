import subprocess
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watchdog.log", encoding="utf-8"),
        logging.StreamHandler()             
    ]
)

# Основной скрипт
SCRIPT_PATH = "main.py"

def run_script():
    process = subprocess.Popen(["python", SCRIPT_PATH])
    logging.info(f"Приложение запущено с PID {process.pid}")
    return process

def watchdog():
    process = run_script()
    try:
        while True:
            if process.poll() is not None:
                logging.warning(f"Оно упало. Поднимаем...")
                process = run_script()
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Остоновка watchdog...")
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        logging.info("Watchdog остановлен.")

if __name__ == "__main__":
    logging.info("Запуск watchdog...")
    watchdog()
