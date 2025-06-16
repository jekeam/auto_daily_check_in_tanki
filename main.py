import io
import logging
import os
import shutil
import sys
import time
import traceback
import uuid
from json.decoder import JSONDecodeError
from logging.handlers import RotatingFileHandler

import psutil
import requests
from PIL import Image
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import NoSuchElementException, SessionNotCreatedException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from config import LOGIN, PASSWORD, RUN_IN_BACKGROUND


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = RotatingFileHandler(log_file, mode="a", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)


setup_logger("main", r"main.log")
log = logging.getLogger("main")


def delete_profile():
    global dir_user_data

    kill_driver_process("")
    time.sleep(10)
    log.info(f"Удаляю временный каталог: {dir_user_data}")
    shutil.rmtree(dir_user_data, ignore_errors=False)


def write_text_to_file_on_desktop(text):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_name = f"ОШИБКА-{str(uuid.uuid1())}.txt"
    file_path = os.path.join(desktop_path, file_name)

    with open(file_path, "w", encoding="UTF-8") as file:
        file.write(text)

    log.error(f"Файл c ошибкой сохранён на рабочем столе под именем: {file_name}")


def set_captcha():
    global DRIVER

    try:
        log.info(f"Проверяем есть ли капча")

        t = 10
        log.info(f"Ждем {t} сек.")
        time.sleep(t)

        id_captcha = DRIVER.find_element(By.ID, "id_captcha")

        captcha_image = DRIVER.find_element(By.CSS_SELECTOR, ".js-captcha-image")
        captcha_url = captcha_image.get_attribute("src")
        if captcha_url and RUN_IN_BACKGROUND:
            write_text_to_file_on_desktop("Требует ввода капчи, запустите код напрямую в RUN_IN_BACKGROUND=False")
            return
        if captcha_url:
            log.info("Обнаружена капча. Необходимо ввести символы с картинки.")
            captcha_response = requests.get(captcha_url)
            img = Image.open(io.BytesIO(captcha_response.content))
            img.show()

            log.info("Ввод капчи пользователем")
            captcha_code = input("Пожалуйста, введите символы с картинки: ")
            log.info("Введена каптча: " + str(captcha_code))

            log.info("Ввод капчи в поле на странице")
            id_captcha.send_keys(captcha_code)
    except NoSuchElementException:
        pass
        log.info("Капча не обнаружена. Продолжаем логин.")
    except Exception as e:
        log.info(f"Ошибка: {e}")
        return


def check_error():
    global DRIVER

    t = 10
    log.info(f"Ждем {t} сек.")
    time.sleep(t)

    try:
        error_message_element = DRIVER.find_element(By.CSS_SELECTOR, ".js-form-errors-content")
        if error_message_element:
            log.info(f"Ошибка: {error_message_element.text}")
            if (
                "Неверный email или пароль" in error_message_element.text
                or "Слишком много" in error_message_element.text
            ):
                return
    except NoSuchElementException:
        pass


def driver_init(headless: bool = 1):
    global DRIVER, dir_user_data

    options = webdriver.ChromeOptions()

    if headless:
        # options.add_argument("--headless")
        options.add_argument("--headless=new")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        # options.add_argument("--disable-dev-shm-usage")
        if os.name != "nt":
            options.add_argument("--no-sandbox")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_argument("start-maximized")
    options.add_argument("--window-size=1920, 1080")

    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={UserAgent().chrome}")

    options.add_argument(f"user-data-dir={dir_user_data}")
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--log-level=3")

    try:
        path_manager = ChromeDriverManager().install()
    except PermissionError as e:
        kill_driver_process(e)
        path_manager = ChromeDriverManager().install()

    set_driver(options, path_manager)

    stealth(
        DRIVER,
        languages=["en-US", "en", "ru"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    log.info(
        f"create new DRIVER: {DRIVER}\n"
        f'navigator.webdriver: {DRIVER.execute_script("return navigator.webdriver;")}\n'
        f'navigator.languages: {DRIVER.execute_script("return navigator.languages;")}\n'
        f'Plugins: {DRIVER.execute_script("return JSON.stringify(Array.from(navigator.plugins).map(p => p.name));")}\n'
        f'UA: {DRIVER.execute_script("return navigator.userAgent;")}\n'
    )


def set_driver(options, path_manager):
    global DRIVER

    try:
        DRIVER = webdriver.Chrome(
            service=ChromeService(os.path.join(os.path.dirname(path_manager), "chromedriver.exe")),
            options=options,
        )
    except SessionNotCreatedException as e:
        log.info(f"Ошибка: {e}, закройте браузер chrome и убейте всего его процессы, после чего повторите попытку.")
        kill_driver_process(e)
        DRIVER = webdriver.Chrome(
            service=ChromeService(os.path.join(os.path.dirname(path_manager), "chromedriver.exe")),
            options=options,
        )


def kill_driver_process(e):
    log.error(f"Получена ошибка доступа: {e}, пробуем убить только процессы Selenium")
    try:
        chromedriver_pid = DRIVER.service.process.pid
        chromedriver = psutil.Process(chromedriver_pid)
        children = chromedriver.children(recursive=True)
        for child in children:
            log.info(f"Убиваем дочерний процесс: {child.name()} (PID {child.pid})")
            child.kill()
        log.info(f"Убиваем chromedriver: {chromedriver.name()} (PID {chromedriver.pid})")
        chromedriver.kill()
    except Exception as e:
        log.error(f"Ошибка при завершении процессов: {e}\n{traceback.format_exc()}")


def make_checkin():
    global DRIVER, dir_user_data

    log.info(f"Открывает страницу {URL}")
    DRIVER.get(URL)

    for _ in range(10):
        t = 10
        log.info(f"Ждем {t} сек.")
        time.sleep(t)

        log.info("Текущая страница: " + DRIVER.current_url)

        try:
            log.info("Проверка подписки на уведомления от модального окна.")
            modal = DRIVER.find_element(By.ID, "modal")
            close_button = DRIVER.find_element(By.ID, "cross")

            if modal.is_displayed():
                log.info("Модальное окно найдено! Закрываю...")
                close_button.click()
                time.sleep(1)
            else:
                log.info("Модальное окно не найдено.")

        except NoSuchElementException:
            log.info("Модальное окно или кнопка закрытия не найдены.")

        try:
            log.info("Проверяем наличие блока уведомления")
            alert = DRIVER.find_element(By.CLASS_NAME, "cm-browsers-alert")
            close_button = DRIVER.find_element(By.CLASS_NAME, "cm-close__browsers")  # Кнопка закрытия

            if alert.is_displayed():
                log.info("Уведомление найдено! Закрываю...")
                close_button.click()

                time.sleep(1)
                log.info("Уведомление успешно закрыто.")
            else:
                log.info("Уведомления нет, ничего закрывать не нужно.")

        except NoSuchElementException:
            log.info("Уведомление или кнопка закрытия не найдены, возможно, оно не появилось.")

        try:
            log.info(f"Проверяем залогинены мы или нет")
            login_link = DRIVER.find_element(By.ID, "login_btn_new")

            log.info(f"Кликаем на кнопку 'Войти'")
            login_link.click()

            t = 10
            log.info(f"Ждем редиректа {t} сек.")
            time.sleep(t)
        except (NoSuchElementException, ElementNotInteractableException) as e:
            log.error(f"{e}: {traceback.format_exc()}")
            delete_profile()
            raise

        try:
            log.info(f"Ищем поля логин и пароль")
            login_field = DRIVER.find_element(By.ID, "id_login")
            password_field = DRIVER.find_element(By.ID, "id_password")

            log.info(f"Очистка полей логин и пароль перед заполнением")
            login_field.send_keys(Keys.CONTROL + "a")
            login_field.send_keys(Keys.DELETE)

            password_field.send_keys(Keys.CONTROL + "a")
            password_field.send_keys(Keys.DELETE)

            log.info(f"Заполняем логин и пароль")
            login_field.send_keys(LOGIN)
            password_field.send_keys(PASSWORD)

            log.info(f"Ставим галочку 'Запомнить меня'")
            remember_checkbox = DRIVER.find_element(By.CSS_SELECTOR, "[for='id_remember']")
            remember_checkbox.click()

            set_captcha()

            log.info(f"Нажатие на кнопку 'Войти'")
            submit_button = DRIVER.find_element(By.CSS_SELECTOR, "button.button-airy")
            if not submit_button:
                delete_profile()
            else:
                submit_button.click()

            check_error()

            t = 10
            log.info(f"Ждем {t} сек.")
            time.sleep(t)

            log.info(f"Проверяем есть ли 2FA")
            is_2fa = DRIVER.find_element(By.ID, "id_code")
            success_2fa = False
            if is_2fa and RUN_IN_BACKGROUND:
                write_text_to_file_on_desktop("Требуется 2FA, запустите код напрямую в RUN_IN_BACKGROUND=False")
                return
            if is_2fa:
                log.info(f"Вводим ключ от 2FA")
                max_attempt = 10
                for r in range(max_attempt):
                    log.info(f"Попытка {r} из {max_attempt}")

                    code_2fa = input("Введите ваш код от 2FA:")

                    log.info(f"Введен код 2FA: " + code_2fa)
                    is_2fa.send_keys(code_2fa)
                    is_2fa.send_keys(Keys.RETURN)

                    t = 10
                    log.info(f"Ждем {t} сек.")
                    time.sleep(t)

                    error_message_element = DRIVER.find_element(By.CSS_SELECTOR, ".js-form-errors-content")
                    if error_message_element:
                        check_error()
                    else:
                        success_2fa = True
                        break

                if not success_2fa:
                    log.info("Коды введены неверно, завершаю работу")
                    return
                else:
                    log.info("Коды введен успешно")

            n = 10
            log.info(f"Ждем {n} сек.")
            time.sleep(n)
        except NoSuchElementException:
            pass

        try:
            log.info(f"Ищем и нажимаем на награду который надо получить")
            first_element = DRIVER.find_element(By.CSS_SELECTOR, ".c_item.c_default")
            first_element.click()

            t = 10
            log.info(f"Ждем {t} сек.")
            time.sleep(t)

            log.info(f"Извлекаем данные из полученной награды")
            task_block = DRIVER.find_element(By.CSS_SELECTOR, ".c_task__body.c_task__comlete")
            title = task_block.find_element(By.CSS_SELECTOR, ".c_task__title").text
            sub_title = task_block.find_element(By.CSS_SELECTOR, ".c_task__sub-title").text
            reward_text = task_block.find_element(By.CSS_SELECTOR, ".c_task__text p").text

            log.info(f"Заголовок: {title}")
            log.info(f"Подзаголовок: {sub_title}")
            log.info(f"Текст награды: {reward_text}")
            log.info(f"Завершаем скрипт")
            return
        except NoSuchElementException:
            log.info("Вероятно отметка уже получена или не прогрузилась страница или завис кеш, проверяем")

            log.info("Проверяем наличие уже полученных наград, когда кеш зависает их нет.")
            el_comlete = DRIVER.find_elements(By.CSS_SELECTOR, ".c_item.c_comlete")

            # todo: возможно надо просто сделать выход и вход в лк, по советку юшки: https://t.me/protanki_yusha/5831
            if not el_comlete:
                log.info("Элементы не найдены, очищаю кеш...")
                delete_profile()
            else:
                log.info(f"Найдено {len(el_comlete)} полученных наград. Очистка кеша не требуется.")

        try:
            DRIVER.find_element(By.CSS_SELECTOR, ".c_item.c_comlete")
            log.info("Отметка уже получена, завершаем работу")

            DRIVER.find_element(By.CSS_SELECTOR, ".c_item.c_disable")
            log.info("Найдена отметка которую надо получить завтра")

            curr_page = DRIVER.current_url.lower()
            allow_page = URL.lower()
            if curr_page != allow_page:
                log.info(
                    f"Ошибка, что то пошло не так, текущая страница ({curr_page}) "
                    f"!= ожидаемой странице ({allow_page})!"
                )

            DRIVER.quit()
            sys.exit()
        except NoSuchElementException:
            log.info("Проверка на наличие уже полученной отметки не удалась, обновляем страницу")
            DRIVER.refresh()
    return


URL = "https://tanki.su/ru/daily-check-in/"

dir_user_data = os.path.join(os.getcwd(), "profile")

DRIVER: ChromiumDriver | None = None

if __name__ == "__main__":
    # todo rewrite on playwright
    try:
        log.info("Запуск драйвера")
        if not RUN_IN_BACKGROUND:
            driver_init(headless=False)

            log.info("Переход на страницу с элементами")
            DRIVER.get(URL)
        else:
            driver_init(headless=True)

        log.info("Начало работы")
        make_checkin()
        DRIVER.quit()
    except JSONDecodeError:
        log.error(traceback.format_exc())
        delete_profile()
    except Exception:
        err_msg = str(traceback.format_exc())
        log.error(err_msg)
        write_text_to_file_on_desktop(err_msg)
    finally:
        if DRIVER:
            log.info("Закрываю браузер")
            DRIVER.quit()
