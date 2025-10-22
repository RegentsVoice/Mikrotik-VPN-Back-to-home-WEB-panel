<img width="1893" height="662" alt="image" src="https://github.com/user-attachments/assets/755fa39f-dab4-48ed-bda5-ec72b1519b27" />
<img width="1893" height="943" alt="image" src="https://github.com/user-attachments/assets/faabe2fe-1e5e-413b-874b-e434f0ce0ef8" />


# Mikrotik VPN Back-to-Home Web Panel

[English](#English) | [Русский](#Русский)

## Русский

### О проекте

Mikrotik VPN Back-to-Home Web Panel — это веб-приложение для управления пользователями функции "Back to Home" на устройствах Mikrotik. Интерфейс создан с использованием библиотеки Gradio и предоставляет удобный способ регистрации, управления и настройки пользователей через браузер.

### Возможности

* Регистрация пользователей: Добавление новых пользователей с указанием имени, расположения и даты деактивации.
* Управление пользователями:
  * Просмотр списка пользователей.
  * Активация/деактивация пользователей.
  * Удаление пользователей.
  * Экспорт конфигурации пользователя.
* Настройки: Изменение параметров подключения (IP-адрес, порт, пароль).
* Логирование: Сохранение логов в файл `watchdog.log` (уровень логирования: INFO).

### Требования

* Python: 3.10.0 (несовместимо с Python 3.12+).
* RouterOS: 7.19 (для версий ниже используйте команду `/ip/cloud/back-to-home-users` вместо `/ip/cloud/back-to-home-user`).
* Библиотеки:
  * `routeros_ssh_connector` — для подключения к Mikrotik через SSH.
  * `gradio` — для создания веб-интерфейса.

### Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel.git
   ```
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Настройте параметры подключения в файле `mikrotik_const.py`:
   ```
   RouteIP = "IP вашего устройства"
   RouteUsername = "Имя пользователя"
   RoutePassword = "Пароль"
   RoutePort = "Порт"
   ```

### Развертывание в Docker

1. Создайте файл `Dockerfile` в корневой директории проекта со следующим содержимым:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 7860
   CMD ["python", "run_web_ui.py"]
   ```
2. Соберите Docker-образ:
   ```
   docker build -t mikrotik-vpn-panel .
   ```
3. Запустите контейнер, указав параметры подключения:
   ```
   docker run -d -p 7862:7862 --name mikrotik-vpn-panel \
   mikrotik-vpn-panel
   ```
4. Откройте веб-интерфейс в браузере по адресу `http://localhost:7860` и войдите:
   * Логин: `Admin`
   * Пароль: `P@ssw0rd`

**Примечание**: Убедитесь, что порт 7860 открыт и доступен. Для изменения параметров подключения используйте переменные окружения или настройте их через веб-интерфейс.

### Запуск

1. Запустите приложение:
   ```
   python run_web_ui.py
   ```
2. Откройте веб-интерфейс в браузере и войдите:
   * Логин: `Admin`
   * Пароль: `P@ssw0rd`

### Настройка

Изменяйте параметры подключения (IP, порт, пароль) через вкладку Настройки в веб-интерфейсе. Убедитесь, что IP-адрес совпадает с адресом устройства или используйте `127.0.0.1` (для Docker — `0.0.0.0`).

### Логирование

Логи сохраняются в файл `watchdog.log` с уровнем логирования INFO.

### Лицензия

Проект распространяется под лицензией MIT License.

### Автор

© 2024 Regent'sVoice

## English

### About

Mikrotik VPN Back-to-Home Web Panel is a web application for managing "Back to Home" users on Mikrotik devices. Built with Gradio, it provides a user-friendly interface for registering, managing, and configuring users via a web browser.

### Features

* User Registration: Add new users with name, location, and deactivation date.
* User Management:
  * View the list of users.
  * Activate/deactivate users.
  * Delete users.
  * Export user configurations.
* Settings: Update connection parameters (IP address, port, password).
* Logging: Logs are saved to `watchdog.log` with INFO level.

### Requirements

* Python: 3.10.0 (incompatible with Python 3.12+).
* RouterOS: 7.19 (for older versions, use `/ip/cloud/back-to-home-users` instead of `/ip/cloud/back-to-home-user`).
* Dependencies:
  * `routeros_ssh_connector` — for SSH connection to Mikrotik.
  * `gradio` — for creating the web interface.

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel.git
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure connection settings in `mikrotik_const.py`:
   ```
   RouteIP = "Your device IP"
   RouteUsername = "Username"
   RoutePassword = "Password"
   RoutePort = "Port"
   ```

### Docker Deployment

1. Create a `Dockerfile` in the project root directory with the following content:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 7860
   CMD ["python", "run_web_ui.py"]
   ```
2. Build the Docker image:
   ```
   docker build -t mikrotik-vpn-panel .
   ```
3. Run the container, specifying connection parameters:
   ```
   docker run -d -p 7862:7862 --name mikrotik-vpn-panel \
   mikrotik-vpn-panel
   ```
4. Open the web interface in your browser at `http://localhost:7860` and log in:
   * Login: `Admin`
   * Password: `P@ssw0rd`

**Note**: Ensure port 7860 is open and accessible. Use environment variables or the web interface to modify connection parameters.

### Usage

1. Run the application:
   ```
   python run_web_ui.py
   ```
2. Open the web interface in your browser and log in:
   * Login: `Admin`
   * Password: `P@ssw0rd`

### Configuration

Update connection parameters (IP, port, password) via the Settings tab in the web interface. Ensure the IP matches the device’s address or use `127.0.0.1` (for Docker, use `0.0.0.0`).

### Logging

Logs are stored in `watchdog.log` with INFO level logging.

### License

This project is licensed under the MIT License.

### Author

© 2024 Regent'sVoice
