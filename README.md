# Mikrotik VPN Back to home WEB panel

![image](https://github.com/user-attachments/assets/4d4ca552-affb-4439-b31d-5f50cf703380)
![image](https://github.com/user-attachments/assets/2483ea56-386e-402b-a683-494094c92a01)


# Mikrotik VPN Back-to-Home Web Panel

[Русский](#русский) | [English](#english)

## Русский

### О проекте

**Mikrotik VPN Back-to-Home Web Panel** — это веб-приложение для управления пользователями функции "Back to Home" на устройствах Mikrotik. Интерфейс создан с использованием библиотеки **Gradio** и предоставляет удобный способ регистрации, управления и настройки пользователей через браузер.

### Возможности

- **Регистрация пользователей**: Добавление новых пользователей с указанием имени, расположения и даты деактивации.
- **Управление пользователями**:
  - Просмотр списка пользователей.
  - Активация/деактивация пользователей.
  - Удаление пользователей.
  - Экспорт конфигурации пользователя.
- **Настройки**: Изменение параметров подключения (IP-адрес, порт, пароль).
- **Логирование**: Сохранение логов в файл `watchdog.log` (уровень логирования: INFO).

### Требования

- **Python**: 3.10.0 (несовместимо с Python 3.12+).
- **RouterOS**: 7.19 (для версий ниже используйте команду `/ip/cloud/back-to-home-users` вместо `/ip/cloud/back-to-home-user`).
- **Библиотеки**:
  - `routeros_ssh_connector` — для подключения к Mikrotik через SSH.
  - `gradio` — для создания веб-интерфейса.

### Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel.git
   ```
2. Установите зависимости:
   ```bash
   pip install routeros_ssh_connector gradio
   ```
3. Настройте параметры подключения в файле `mikrotik_const.py`:
   ```python
   RouteIP = "IP вашего устройства"
   RouteUsername = "Имя пользователя"
   RoutePassword = "Пароль"
   RoutePort = "Порт"
   ```

### Запуск

1. Запустите приложение:
   ```bash
   python run_web_ui.py
   ```
2. Откройте веб-интерфейс в браузере и войдите:
   - **Логин**: `Admin`
   - **Пароль**: `P@ssw0rd`

### Настройка

Изменяйте параметры подключения (IP, порт, пароль) через вкладку **Настройки** в веб-интерфейсе. Убедитесь, что IP-адрес совпадает с адресом устройства или используйте `127.0.0.1` (для Docker — `0.0.0.0`).

### Логирование

Логи сохраняются в файл `watchdog.log` с уровнем логирования INFO.

### Лицензия

Проект распространяется под лицензией [MIT License](LICENSE).

### Автор

© 2024 Regent'sVoice

---

## English

### About

**Mikrotik VPN Back-to-Home Web Panel** is a web application for managing "Back to Home" users on Mikrotik devices. Built with **Gradio**, it provides a user-friendly interface for registering, managing, and configuring users via a web browser.

### Features

- **User Registration**: Add new users with name, location, and deactivation date.
- **User Management**:
  - View the list of users.
  - Activate/deactivate users.
  - Delete users.
  - Export user configurations.
- **Settings**: Update connection parameters (IP address, port, password).
- **Logging**: Logs are saved to `watchdog.log` with INFO level.

### Requirements

- **Python**: 3.10.0 (incompatible with Python 3.12+).
- **RouterOS**: 7.19 (for older versions, use `/ip/cloud/back-to-home-users` instead of `/ip/cloud/back-to-home-user`).
- **Dependencies**:
  - `routeros_ssh_connector` — for SSH connection to Mikrotik.
  - `gradio` — for creating the web interface.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel.git
   ```
2. Install dependencies:
   ```bash
   pip install routeros_ssh_connector gradio
   ```
3. Configure connection settings in `mikrotik_const.py`:
   ```python
   RouteIP = "Your device IP"
   RouteUsername = "Username"
   RoutePassword = "Password"
   RoutePort = "Port"
   ```

### Usage

1. Run the application:
   ```bash
   python run_web_ui.py
   ```
2. Open the web interface in your browser and log in:
   - **Login**: `Admin`
   - **Password**: `P@ssw0rd`

### Configuration

Update connection parameters (IP, port, password) via the **Settings** tab in the web interface. Ensure the IP matches the device’s address or use `127.0.0.1` (for Docker, use `0.0.0.0`).

### Logging

Logs are stored in `watchdog.log` with INFO level logging.

### License

This project is licensed under the [MIT License](LICENSE).

### Author

© 2024 Regent'sVoice
