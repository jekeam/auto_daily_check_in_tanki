## Автоматическое получения отметок ежедневного [табель-календаря](https://tanki.su/ru/daily-check-in/)

> [!NOTE]
> - Помните, чтоб взятые отметки засчитывались, необходимо заходить в игру - каждый день.
> - [ ]  **2FA**: Рекомендую пока использовать только логины пароли без 2FA(т.к. 2FA - пока не поддреживается в нормальном режиме, напишите нормально, через `pyotp.TOTP` - жду MR :)


---
> [!CAUTION]
> Использование представленного кода для автоматизации ежедневного чек-ина или иных действий на официальных ресурсах **Lesta Games** $\textcolor{red}{\textsf{нарушает условия}}$ , изложенные в следующих официальных документах:
>
> - [Лицензионное соглашение с конечным пользователем EULA](https://legal.lesta.ru/eula/)
>   
>   В частности, пункт **6.2.1** данного соглашения запрещает использование сторонних программ, скриптов, ботов или иных автоматизированных средств, изменяющих стандартное поведение игры и её официальных сервисов, включая веб-сайты.
> 
> - [Правила игры и кланов](https://legal.lesta.ru/game-rules/)
>   
>   Согласно пункту **2.1.7** данных правил, запрещается использование любых программ или методов, позволяющих автоматически управлять игровым процессом или получать преимущества без непосредственного участия игрока.
> 
> **Последствия использования данного кода могут включать:**
> - Блокировку или удаление игрового аккаунта;
> - Применение иных санкций со стороны администрации игры.
> 
> **Отказ от ответственности:**  
> Предоставленный код распространяется «как есть», без каких-либо гарантий. Автор не несёт ответственности за любые последствия, возникшие в результате его использования.
> Используйте данный код исключительно на свой страх и риск и только после полного ознакомления с вышеуказанными документами.


---
## Установка
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


---
## Конфигурация перед запуском

Введите ваш логин и пароль в файл [config.py](https://github.com/jekeam/auto_daily_check_in_tanki/blob/master/config.py)
> [!IMPORTANT]
> Программа не передает ни куда ваши данные, вы можете в этом убедиться, посмотреть открытый исходный код


---
## Пример Sheduller для windows

Cкачайте импортируйте в taskschd.msc: [wot.xml](https://github.com/jekeam/auto_daily_check_in_tanki/raw/master/wot.xml)

> [!IMPORTANT]
> Измените путь для pythonw.exe


---
## ❓ FAQ

<details>
<summary><strong>🔴 PermissionError: [Errno 13] Permission denied: 'C:\\Users\\...\\chromedriver.exe'</strong></summary>

**Решение:**

- Завершите все процессы `chromedriver.exe` через Диспетчер задач.
- Очистите каталог `%USERPROFILE%\.wdm`.

</details>


---
<details>
<summary><strong>🔴 PermissionError: [WinError 5] Отказано в доступе</strong></summary>

**Решение:**

- Перезагрузите компьютер.
- Либо завершите все процессы `chromedriver.exe`.

</details>


---
<details>
<summary><strong>🟡 DevTools listening при запуске через pythonw.exe</strong></summary>

Если при запуске через `pythonw.exe` появляется окно:

```
DevTools listening on ws://127.0.0.1:50605/devtools/browser/11c9063a-44ce-4b39-9566-9e6c6270025c
```

**Решение:**

1. Откройте файл:  
   ```
   .\venv\Lib\site-packages\selenium\webdriver\common\service.py
   ```
   > ⚠️ Не перепутайте с `services.py`

2. В функции `start()` замените `subprocess.Popen` так, чтобы он включал флаг `creationflags=0x8000000`.

**Пример:**
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

</details>


---
## 🎥 Видеоинструкция (спасибо Депп)</strong></summary>

[![YouTube Video](https://img.youtube.com/vi/z-5otBFmSMc/0.jpg)](https://www.youtube.com/watch?v=z-5otBFmSMc&t=10s)

