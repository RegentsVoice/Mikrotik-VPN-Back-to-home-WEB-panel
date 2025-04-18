# Mikrotik VPN Back to home WEB panel


Этот инструмент позволяет управлять пользователями на устройстве Mikrotik через веб-интерфейс, созданный с использованием Gradio. Инструмент поддерживает регистрацию новых пользователей, управление существующими пользователями и настройку параметров подключения к web ui.
![image](https://github.com/user-attachments/assets/4d4ca552-affb-4439-b31d-5f50cf703380)
![image](https://github.com/user-attachments/assets/2483ea56-386e-402b-a683-494094c92a01)



## Функциональность

- **Регистрация пользователей**: Добавление новых пользователей с указанием даты деактивации, расположения и имени.
- **Управление пользователями**: Получение списка пользователей, удаление пользователей, переключение состояния пользователей (активация/деактивация), выгрузка конфигурации пользователя.
- **Настройки**: Обновление параметров подключения (IP-адрес, порт, пароль).

## Установка

**Клонируйте репозиторий**:

`git clone https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel.git`

**Установите зависимости**:

`pip install routeros_ssh_connector gradio`


**Отредактируйте**:
`mikrotik_const.py`

RouteIP = "IP вашего устройства"

RouteUsername = "Пользователь"

RoutePassword = "Пароль"

RoutePort = "Порт"
    

## Зависимости

Для запуска вам потребуется:

- `Python 3.10.0`  **Внимание!!! Несовместим с Python 3.12+**
- `routeros_ssh_connector`: Библиотека для подключения к устройству Mikrotik через SSH.
- `gradio`: Библиотека для создания веб-интерфейсов.

## Использование

**Запустите приложение**:

Запустите `run_web_ui.py`

**Введите логин и пароль в открывшемся окне браузера**:

Логин: `Admin`

Пароль: `P@ssw0rd`
    

## Настройка

Параметры подключения (IP-адрес, порт, пароль) можно изменить через вкладку "Настройки" в веб-интерфейсе. Имейте в виду, IP Адрес должен совподать с адресом устройства на котором запушен или иметь значение 127.0.0.1.

## Логирование

Логи сохраняются в файл watchdog.log. Уровень логирования установлен на INFO.

## Лицензия

Этот проект лицензирован под ([MIT License](https://github.com/RegentsVoice/Mikrotik-VPN-Back-to-home-WEB-panel/blob/main/LICENSE.md))

## Автор

© 2024 Regent'sVoice.
