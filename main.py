from routeros_ssh_connector import MikrotikDevice
from const import *
from panelsetting import *
import re, random, string, tempfile, os, signal, logging
import gradio as gr

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watchdog.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

router = None

def contains_cyrillic(text):
    return any(char in text for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

def register_user(UserLocation, UserName, ExpiresYear, ExpiresMonth, ExpiresDay):
    if contains_cyrillic(UserLocation) or contains_cyrillic(UserName):
        return "Используйте только латиницу для ввода данных."

    if not UserLocation or not UserName:
        return "Что-то пошло не так!"

    ExpiresDate = ""
    if ExpiresYear:
        ExpiresDate += ExpiresYear
    if ExpiresMonth:
        ExpiresDate += f"-{ExpiresMonth.zfill(2)}"
    if ExpiresDay:
        ExpiresDate += f"-{ExpiresDay.zfill(2)}"

    try:
        if ExpiresDate:
            command = f"/ip/cloud/back-to-home-users add allow-lan=yes comment={UserLocation} expires={ExpiresDate} name={UserName}"
        else:
            command = f"/ip/cloud/back-to-home-users add allow-lan=yes comment={UserLocation} name={UserName}"
        router.send_command(command)
        logging.info(f"Пользователь '{UserName}' зарегистрирован.")
        return f"Пользователь '{UserName}' Успешно зарегистрирован."
    except Exception as e:
        logging.error(f"Ошибка при регистрации '{UserName}': {str(e)}")
        return f"Что-то пошло не так: {str(e)}"

def get_user_list():
    try:
        response = router.send_command("/ip/cloud/back-to-home-users print")
        users = []
        comment = ""
        user_id = None

        for line in response.split("\n"):
            logging.debug(f"Processing line: {line}")
            if line.lstrip().startswith(";;;"):
                comment = line.lstrip()[4:].strip()

            elif line.lstrip().startswith(tuple(str(i) for i in range(10))):
                parts = line.split()
                user_id = parts[0]
                flag = parts[1]
                name = parts[2]
                expires = parts[3]
                expires = "Никогда" if expires == "never" else expires
                users.append([user_id, name, "Активен" if flag == "A" else "Деактивирован", comment, expires])
                comment = "" 
        return users
    except Exception as e:
        logging.error(f"Ошибка при выводе списка пользователей: {str(e)}")
        return [[f"Что-то пошло не так: {str(e)}"]]

def delete_user_by_number(user_number):
    if not user_number.isdigit():
        return "Укажите корректный номер пользователя."
    command = f"/ip/cloud/back-to-home-users remove numbers={user_number}"
    try:
        router.send_command(command)
        logging.info(f"Пользователь с номером '{user_number}' удалён")
        return f"Пользователь с номером '{user_number}' успешно удалён."
    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя с номером '{user_number}': {str(e)}")
        return f"Ошибка при удалении пользователя: {str(e)}"

def export_user_config(user_number):
    if not user_number:
        return "Введите номер пользователя."
    command = f"/ip/cloud/back-to-home-users show-client-config number={user_number}"
    try:
        response = router.send_command(command)
        lines = response.splitlines()
        start_idx = next((i for i, line in enumerate(lines) if line.startswith("[Interface]")), None)
        end_idx = next((i for i, line in enumerate(lines) if line.startswith("qr:")), None)
        config_lines = lines[start_idx:end_idx]
        return "\n".join(config_lines)
    except Exception as e:
        logging.error(f"Ошибка при выгрузке конфигурации: {str(e)}")
        return f"Ошибка при выгрузке конфигурации: {str(e)}"

def save_config_to_file(config_content):
    if not config_content.strip():
        logging.error(f"Ошибка создания файла конфигурации Wireguard - Конфигурация пуста")
        raise ValueError("Конфигурация пуста.")

    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="WG-VPN-", suffix=".conf", mode="w", encoding="utf-8")
    temp_file.write(config_content)
    temp_file.close()
    logging.info(f"Создан файл конфигурации Wireguard")
    return temp_file.name

def toggle_user_state(user_number, action):
    if not user_number.isdigit():
        return "Укажите корректный номер пользователя."
    command = f"/ip/cloud/back-to-home-users {'enable' if action == 'Activate' else 'disable'} numbers={user_number}"
    try:
        router.send_command(command)
        logging.info(f"Пользователь с номером '{user_number}' {'активирован' if action == 'Activate' else 'деактивирован'}.")
        return f"Пользователь с номером '{user_number}' успешно {'активирован' if action == 'Activate' else 'деактивирован'}."
    except Exception as e:
        logging.error(f"Ошибка при переключении состояния: {str(e)}")
        return f"Ошибка при переключении состояния: {str(e)}"

def update_settings(ip=None, port=None, password=None):
    try:
        with open("panelsetting.py", "r") as file:
            lines = file.readlines()
        current_settings = {"ip": None, "port": None, "password": None}
        for line in lines:
            if line.startswith("GServerIp"):
                current_settings["ip"] = re.search(r'"(.*?)"', line).group(1)
            elif line.startswith("GServerPort"):
                current_settings["port"] = int(re.search(r"(\d+)", line).group(1))
            elif line.startswith("GPassword"):
                current_settings["password"] = re.search(r'"(.*?)"', line).group(1)
        for i, line in enumerate(lines):
            if line.startswith("GServerIp"):
                new_ip = ip if ip else current_settings["ip"]
                lines[i] = f'GServerIp = "{new_ip}"\n'
            elif line.startswith("GServerPort"):
                new_port = port if port else current_settings["port"]
                lines[i] = f'GServerPort = {new_port}\n'
            elif line.startswith("GPassword"):
                new_password = password if password else current_settings["password"]
                lines[i] = f'GPassword = "{new_password}"\n'
        with open("panelsetting.py", "w") as file:
            file.writelines(lines)

        logging.info(f"Изменены настройки приложения")
        return "Настройки успешно обновлены."
    except Exception as e:
        logging.error(f"Ошибка при изменении настроек приложения: {e}")
        return f"Ошибка при обновлении настроек: {e}"

def stopapp():
    os.kill(os.getpid(), signal.SIGTERM)

def settings_interface():
    with gr.Blocks() as settings_tab:
        gr.Markdown("**Внимание:** После внесения любых изменений перезапустите приложение.")
        with gr.Row():
            ip_input = gr.Textbox(label="IP-адрес сервера", placeholder="Введите новый IP-адрес")
            port_input = gr.Textbox(label="Порт сервера", value=None, placeholder="Введите новый порт")
            password_input = gr.Textbox(label="Пароль", type="password", placeholder="Введите новый пароль")
        with gr.Row():
            save_button = gr.Button("Сохранить настройки")
            restart_button = gr.Button("Перезапустить приложение")
        status_output = gr.Textbox(label="Результат", interactive=False)
        save_button.click(
            update_settings,
            inputs=[ip_input, port_input, password_input],
            outputs=[status_output]
        )
        restart_button.click(fn=stopapp)
        with gr.Blocks():
            gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")
    return settings_tab

settings_tab = settings_interface()

with gr.Blocks() as manage_tab:
    with gr.Column():
        load_users_button = gr.Button("Получить пользователей")
        user_list_output = gr.DataFrame(label="Список пользователей", headers=["Номер", "Имя", "Статус", "Подразделение", "Дата истечения"])
        load_users_button.click(get_user_list, outputs=user_list_output)

        gr.Markdown("<hr style='border: 1px solid #ccc;'>")

        with gr.Row():
            user_number_input = gr.Textbox(label="Номер пользователя", placeholder="Введите номер пользователя", scale=1)
            action_radio = gr.Radio(
                label="Действие",
                choices=["Активировать", "Деактивировать", "Удалить", "Выгрузить конфигурацию"],
                value="Активировать",
                scale=3
            )
            action_button = gr.Button("Выполнить действие", scale=1)

        result_output = gr.Textbox(label="Результат операции", interactive=False)
        download_file = gr.File(label="Скачайте файл конфигурации")

        def handle_action(number, action):
            if not number:
                return ("Введите номер пользователя", None)

            if action == "Активировать":
                result = toggle_user_state(number, "Activate")
                return (result, None)
            elif action == "Деактивировать":
                result = toggle_user_state(number, "Deactivate")
                return (result, None)
            elif action == "Удалить":
                result = delete_user_by_number(number)
                return (result, None)
            elif action == "Выгрузить конфигурацию":
                config = export_user_config(number)
                file_path = save_config_to_file(config)
                return ("Конфигурация успешно выгружена", file_path)

            return ("Неизвестное действие", None)

        action_button.click(
            handle_action,
            inputs=[user_number_input, action_radio],
            outputs=[result_output, download_file]
        )

        with gr.Blocks():
            gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")

with gr.Blocks() as register_tab:
    with gr.Column():
        gr.Markdown("**Внимание:** Используйте только латиницу для ввода данных.")

        UserLocation = gr.Textbox(label="Расположение пользователя", placeholder="Введите расположение пользователя латиницей")
        UserName = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя латиницей")

        gr.Markdown("Дата истечения опциональна.")
        with gr.Row():
            ExpiresYear = gr.Textbox(label="Год", placeholder="Год", scale=1)
            ExpiresMonth = gr.Textbox(label="Месяц", placeholder="Месяц", scale=1)
            ExpiresDay = gr.Textbox(label="День", placeholder="День", scale=1)

        register_button = gr.Button("Зарегистрировать пользователя")
        result_output = gr.Textbox(label="Результат регистрации", interactive=False)

        register_button.click(
            fn=register_user,
            inputs=[UserLocation, UserName, ExpiresYear, ExpiresMonth, ExpiresDay],
            outputs=result_output
        )

        with gr.Blocks():
            gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")

app = gr.TabbedInterface(
    interface_list=[register_tab, manage_tab, settings_tab],
    tab_names=["Регистрация пользователей", "Управление пользователями", "Настройки"],
    title="MikroTik WEB"
)

app.css = """
    footer {display: none !important;}
    """

def connect_to_router():
    global router
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        logging.info(f"Успешное подключение к устройству с параметрами: IP={RouteIP}, Port={RoutePort}, Username={RouteUsername}")
    except Exception as e:
        logging.error(f"Ошибка при подключении к устройству: {str(e)}")
        raise

connect_to_router()
app.launch(server_name=GServerIp, server_port=GServerPort, show_api=False, auth=(f"Admin", GPassword))
