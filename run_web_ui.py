import subprocess
import time
import logging
import webbrowser
import importlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watchdog.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

SCRIPT_PATH = "main.py"

def run_script(GServerIp, GServerPort):
    process = subprocess.Popen(["python", SCRIPT_PATH])
    logging.info(f"Приложение запущено с PID {process.pid} Ожидайте открытия окна приложения")
    time.sleep (5)
    url = f"http://{GServerIp}:{GServerPort}"
    logging.info(f"Открытие браузера с адресом: {url}")
    webbrowser.open(url)
    return process

def watchdog():
    import web_ui_const
    GServerIp = web_ui_const.GServerIp
    GServerPort = web_ui_const.GServerPort
    process = run_script(GServerIp, GServerPort)

    try:
        while True:
            if process.poll() is not None:
                logging.warning(f"Оно упало. Поднимаем...")
                importlib.reload(web_ui_const)
                GServerIp = web_ui_const.GServerIp
                GServerPort = web_ui_const.GServerPort
                process = run_script(GServerIp, GServerPort)

            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Остоновка watchdog...")
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        logging.info("Watchdog остановлен.")


logging.info("Запуск watchdog...")
watchdog()
