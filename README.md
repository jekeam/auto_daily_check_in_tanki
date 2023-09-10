# Auto daily check in tanki
Скрипт для автоматического получения отметок ежедневного табель-календаря wot/tanki

# Установка
1. Установите Python версии 3.11, следуя инструкциям с официального сайта
   Python: [https://www.python.org](https://www.python.org).

2. Клонируйте репозиторий на вашем локальном компьютере:
    ```shell
    git clone https://github.com/jekeam/auto_daily_check_in_tanki.git
    ```

3. Перейдите в директорию проекта:
    ```shell
    cd auto_daily_check_in_tanki
    ```

4. Рекомендуется создать виртуальное окружение для изоляции зависимостей:
    ```shell
    python -m venv venv
    ```

5. Активируйте виртуальное окружение:
    1. Linux
        ```shell
        source venv/bin/activate
        ```

    2. Windows:
        ```shell
        venv\Scripts\activate.bat
        ```
       **Примечание:** Если вы используете PowerShell или не можете активировать виртуальное окружение с помощью `venv\Scripts\activate.bat`,
       попробуйте выполнить следующую команду:
        ```shell
        .\venv\Scripts\Activate.ps1
        ```

6. Установите зависимости, указанные в файле `requirements.txt`:
    ```shell
    python -m pip install -r requirements.txt
    ```
   
# Конфигурация перед запуском
Введите ваш логин и пароль в файл config.py

#  FAQ

## PermissionError: [WinError 5] Отказано в доступе
При возникновении ошибки, попробуйте перезагрузить ПК (либо убить все процессы c chromedriver.exe)

## Output: Если вы запускате задау в безшумном режиме через pythonw.exe и вылазит окно: DevTools listening on ws://127.0.0.1:50605/devtools/browser/11c9063a-44ce-4b39-9566-9e6c6270025c
Отредактируйте файл: ```.\venv\Lib\site-packages\selenium\webdriver\common\service.py``` (Not services.py, its service.py)

В функции ```start()``` установить для Popen:
```creationflags=0x8000000```
