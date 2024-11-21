from routeros_ssh_connector import MikrotikDevice
from const import *
from panelsetting import *
import re, random, string, tempfile, os, signal, logging
import gradio as gr

# Отключаем сбор статистики на стороне gradio
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watchdog.log", encoding="utf-8"),
        logging.StreamHandler()             
    ]
)

# Функция для автоматического добавления дефисов в дату
def format_date(date_str):
    date_str = ''.join(c for c in date_str if c.isdigit())
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str

# Функция для регистрации нового пользователя
def register_user(ExpiresDate, UserLocation, UserName):
    if not ExpiresDate or not UserLocation or not UserName:
        return "Что-то пошло не так!"
    
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        router.send_command(f"/ip/cloud/back-to-home-users add allow-lan=yes comment={UserLocation} expires={ExpiresDate} name={UserName}")
        router.disconnect()
        logging.info(f"Пользователь '{UserName}' зарегистрирован.")
        return f"Пользователь '{UserName}' Успешно зарегистрирован."
    except Exception as e:
        logging.info(f"Ошибка при регистрации '{UserName}'")
        return f"Что-то пошло не так: {str(e)}"
    finally:
        del router

# Функция для получения списка пользователей
def get_user_list():
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        response = router.send_command("/ip/cloud/back-to-home-users print")
        router.disconnect()
        users = []
        comment = ""  
        user_id = None  

        for line in response.split("\n"):
            # Если строка начинается с ';;;', то это комментарий
            if line.lstrip().startswith(";;;"):
                comment = line.lstrip()[4:].strip() 

            # Если строка содержит данные пользователя (начинается с номера)
            elif line.lstrip().startswith(tuple(str(i) for i in range(10))):
                parts = line.split()
                user_id = parts[0]
                flag = parts[1]
                name = parts[2]
                expires = parts[3]
                expires = "Никогда" if expires == "never" else expires
                users.append([user_id, name, "Активен" if flag == "A" else "Деактивирован", comment, expires])
                comment = ""  # Сбрасываем комментарий для следующего пользователя
        return users
    except Exception as e:
        logging.info(f"Ошибка при выводе списка пользователей {str(e)}")
        return [[f"Что-то пошло не так: {str(e)}"]]
    finally:
        del router

# Функция для удаления пользователя по номеру
def delete_user_by_number(user_number):
    if not user_number.isdigit():
        return "Укажите корректный номер пользователя."
    command = f"/ip/cloud/back-to-home-users remove numbers={user_number}"
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        router.send_command(command)
        router.disconnect()
        logging.info(f"Пользователь с номером '{user_number}' удалён")
        return f"Пользователь с номером '{user_number}' успешно удалён."
    except Exception as e:
        logging.info(f"Ошибка при удалении пользователя с номером '{user_number}'")
        return f"Ошибка при удалении пользователя: {str(e)}"
    finally:
        del router

# Функция выгрузки конфигурации пользователя
def export_user_config(user_number):
    if not user_number:
        return "Введите номер пользователя."
    command = f"/ip/cloud/back-to-home-users show-client-config number={user_number}"
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        response = router.send_command(command)
        router.disconnect()
        lines = response.splitlines()
        start_idx = next((i for i, line in enumerate(lines) if line.startswith("[Interface]")), None)
        end_idx = next((i for i, line in enumerate(lines) if line.startswith("qr:")), None)
        config_lines = lines[start_idx:end_idx]
        return "\n".join(config_lines)
    except Exception as e:
        return f"Ошибка при выгрузке конфигурации: {str(e)}"
    finally:
        del router

# Функция создания файла конфигурации
def save_config_to_file(config_content):
    if not config_content.strip():
        logging.info(f"Ошибка создания файла конфигурации Wireguard - Конфигурация пуста")
        raise ValueError("Конфигурация пуста.")

    # Создаём временный файл
    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="WG-VPN-", suffix=".conf", mode="w", encoding="utf-8")
    temp_file.write(config_content)
    temp_file.close()
    logging.info(f"Создан файл конфигурации Wireguard")
    return temp_file.name
  
# Функция для переключения состояния пользователя по номеру
def toggle_user_state(user_number, action):
    if not user_number.isdigit():
        return "Укажите корректный номер пользователя."
    command = f"/ip/cloud/back-to-home-users {'enable' if action == 'Activate' else 'disable'} numbers={user_number}"
    router = MikrotikDevice()
    try:
        router.connect(RouteIP, RouteUsername, RoutePassword, RoutePort)
        router.send_command(command)
        router.disconnect()
        logging.info(f"Пользователь с номером '{user_number}' {'активирован' if action == 'Activate' else 'деактивирован'}.")
        return f"Пользователь с номером '{user_number}' успешно {'активирован' if action == 'Activate' else 'деактивирован'}."
    except Exception as e:
        logging.info(f"Ошибка при переключении состояния: {str(e)}")
        return f"Ошибка при переключении состояния: {str(e)}"
    finally:
        del router

# Функция обновления настроек
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
        logging.info(f"Ошибка при изменении настроек приложения")
        return f"Ошибка при обновлении настроек: {e}"
# Функция остановки прилржения        
def stopapp():
    os.kill(os.getpid(),
    signal.SIGTERM)

# Интерфейс вкладки настроек
def settings_interface():
    with gr.Blocks() as settings_tab:
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

# Вкладка для управления пользователями
with gr.Blocks() as manage_tab:
    with gr.Column():
        load_users_button = gr.Button("Получить пользователей")
        user_list_output = gr.DataFrame(label="Список пользователей", headers=["Номер", "Имя", "Статус", "Подразделение", "Дата истечения"])
        load_users_button.click(fn=get_user_list, inputs=[], outputs=user_list_output)
        
        gr.Markdown("<hr style='border: 1px solid #ccc;'>")
        
        toggle_user_input = gr.Textbox(label="Номер пользователя для переключения состояния", placeholder="Введите номер пользователя")
        toggle_action = gr.Radio(label="Действие", choices=["Activate", "Deactivate"], value="Activate")
        toggle_button = gr.Button("Применить действие")
        toggle_output = gr.Textbox(label="Результат переключения состояния")
        toggle_button.click(fn=toggle_user_state, inputs=[toggle_user_input, toggle_action], outputs=toggle_output)
        
        gr.Markdown("<hr style='border: 1px solid #ccc;'>")
        
        delete_user_input = gr.Textbox(label="Номер пользователя для удаления", placeholder="Введите номер пользователя")
        delete_button = gr.Button("Удалить пользователя")
        delete_output = gr.Textbox(label="Результат удаления")
        delete_button.click(fn=delete_user_by_number, inputs=[delete_user_input], outputs=delete_output)
        
        gr.Markdown("<hr style='border: 1px solid #ccc;'>")
        
        gr.Markdown("### Выгрузка конфигурации")
        user_number_input = gr.Textbox(label="Номер пользователя для выгрузки конфигурации", placeholder="Введите номер пользователя")
        export_button = gr.Button("Выгрузить конфигурацию")
        config_output = gr.Textbox(label="Конфигурация", interactive=False, lines=10)
        export_button.click(fn=export_user_config, inputs=[user_number_input], outputs=config_output)
        save_button = gr.Button("Сохранить конфигурацию")
        download_file = gr.File(label="Скачайте файл конфигурации")
        save_button.click(
            fn=save_config_to_file,
            inputs=[config_output],
            outputs=[download_file]
        )
        with gr.Blocks():
            gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")

# Интерфейс для регистрации пользователей
with gr.Blocks() as register_tab:
    with gr.Column():
        # Ввод данных
        ExpiresDate = gr.Textbox(label="Дата деактивации", placeholder="Год-месяц-день")
        UserLocation = gr.Textbox(label="Расположение пользователя", placeholder="Введите расположение пользователя латиницей")
        UserName = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя латиницей")
        register_button = gr.Button("Зарегистрировать пользователя")
        result_output = gr.Textbox(label="Результат регистрации", interactive=False)
        register_button.click(
            fn=register_user,
            inputs=[ExpiresDate, UserLocation, UserName],
            outputs=result_output
        )
        ExpiresDate.change(fn=format_date, inputs=ExpiresDate, outputs=ExpiresDate)
        with gr.Blocks():
            gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")

# Функция для генерации паролей
def generate_password(length, use_uppercase, use_numbers, use_special, exclude_special):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    exclude_chars = "~'\"/\\|.,-oO;:<>{}[]^`"
    if exclude_special:
        characters = ''.join(c for c in characters if c not in exclude_chars)
    if length <= 0:
        return "Длина пароля должна быть больше 0"
    password = ''.join(random.choice(characters) for _ in range(length))
    logging.info(f"Сгенерирован пароль")
    return password

# Интерфейс для генератора паролей
with gr.Blocks() as pas_tab:
    with gr.Column():
        length = gr.Slider(label="Длина пароля", minimum=6, maximum=32, value=8, step=1)
        use_uppercase = gr.Checkbox(label="Включить заглавные буквы", value=True)
        use_numbers = gr.Checkbox(label="Включить цифры", value=True)
        use_special = gr.Checkbox(label="Включить специальные символы", value=True)
        exclude_special = gr.Checkbox(label="Отключить символы ~'`\"/\\|.,-oO;:<>{}[]^", value=True)
        generate_button = gr.Button("Сгенерировать пароль")
        password_output = gr.Textbox(label="Сгенерированный пароль", interactive=False)
        generate_button.click(
            fn=generate_password,
            inputs=[length, use_uppercase, use_numbers, use_special, exclude_special],
            outputs=[password_output]
        )
    with gr.Blocks():
        gr.HTML("<p style='text-align:center;'>© 2024 Regent'sVoice.</p>")

# Основной интерфейс
app = gr.TabbedInterface(
    interface_list=[register_tab, manage_tab, pas_tab, settings_tab],
    tab_names=["Регистрация пользователей", "Управление пользователями", "Генератор паролей", "Настройки"],
    title="MikroTik WEB"
)

app.css = """
    footer {display: none !important;}
    """

app.launch(server_name=GServerIp, server_port=GServerPort, show_api=False, auth=(f"Admin", GPassword))
