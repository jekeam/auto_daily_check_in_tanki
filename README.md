# Auto daily check in tanki
Скрипт для автоматического получения отметок ежедневного табель-календаря https://tanki.su/ru/daily-check-in

> [!WARNING]
> Помните, чтоб взятые отметки засчитывались, необходимо заходить в игру - каждый день.

> [!NOTE]
> Рекомендую пока использовать только логины пароли без 2FA(т.к. 2FA - пока не поддреживается в нормальном режиме, напишите нормально, через `pyotp.TOTP` - жду MR :)

# Установка
1. Установите Python версии 3.11, следуя инструкциям с официального сайта
   Python: https://www.python.org/downloads/release/python-3115/.

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
(Программа не передает ни куда ваши данные, вы можете в этом убедиться, посмотреть открытый исходный код)

# Автоматизация
Прикладываю пример Sheduller для  windows - скачайте импортируйте в taskschd.msc (Измените путь для pythonw.exe)
[wot.xml](https://github.com/jekeam/auto_daily_check_in_tanki/raw/master/wot.xml)

#  FAQ

## PermissionError: [Errno 13] Permission denied: 'C:\\Users\\....\\chromedriver.exe'
Убейте все процесс с `chromedriver.exe` и почистите каталог `%USERPROFILE%.\.wdm`



## PermissionError: [WinError 5] Отказано в доступе
При возникновении ошибки, попробуйте перезагрузить ПК (либо убить все процессы c chromedriver.exe)

## Output: Если вы запускате задау в безшумном режиме через pythonw.exe и вылазит окно: DevTools listening on ws://127.0.0.1:50605/devtools/browser/11c9063a-44ce-4b39-9566-9e6c6270025c
Отредактируйте файл: ```.\venv\Lib\site-packages\selenium\webdriver\common\service.py``` (Not services.py, its service.py)

В функции ```start()``` установить число 0x8000000 (это именно число - не строка) - для Popen:
```creationflags=0x8000000```

Пример:
```python
        try:
            cmd = [self.path]
            cmd.extend(self.command_line_args())
            self.process = subprocess.Popen(cmd, env=self.env,
                                            close_fds=system() != 'Windows',
                                            stdout=self.log_file,
                                            stderr=self.log_file,
                                            stdin=PIPE,
                                            creationflags=0x8000000)
        except TypeError:
            raise
```

# Видео инструкция (Спасибо Депп)
https://www.youtube.com/watch?v=z-5otBFmSMc&t=10s


