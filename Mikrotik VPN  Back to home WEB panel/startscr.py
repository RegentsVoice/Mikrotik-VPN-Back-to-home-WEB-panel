import subprocess
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: INFO
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watchdog.log", encoding="utf-8"),
        logging.StreamHandler()             
    ]
)

# Основной скрипт
SCRIPT_PATH = "main.py"

def run_script():
    # Запуск основной тушки
    process = subprocess.Popen(["python", SCRIPT_PATH])
    logging.info(f"Приложение запущено с PID {process.pid}")
    return process

def watchdog():
    #Следит за вторым скриптом и перезапускает его при падении
    process = run_script()  # Запускаем скрипт первый раз
    
    try:
        while True:
            # Проверяем, работает ли процесс
            if process.poll() is not None:  # Если процесс завершился
                logging.warning(f"Оно упало. Поднимаем...")
                process = run_script()  # Перезапуск
            
            time.sleep(5)  # Проверяем состояние каждые 5 секунд
    except KeyboardInterrupt:
        logging.info("Остоновка watchdog...")
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        logging.info("Watchdog остановлен.")

if __name__ == "__main__":
    logging.info("Запуск watchdog...")
    watchdog()
