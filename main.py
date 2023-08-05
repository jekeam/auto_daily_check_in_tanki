import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from config import LOGIN, PASSWORD


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fileHandler = RotatingFileHandler(log_file, mode="a", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf8")
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


setup_logger("main", r"main.log")
log = logging.getLogger("main")


def driver_init(headless: bool = 1):
    options = webdriver.ChromeOptions()

    dir_user_data = os.path.join(os.getcwd(), "profile")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if os.name != "posix":
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_argument("start-maximized")
    options.add_argument("--window-size=1920, 1080")

    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    )

    options.add_argument(f"user-data-dir={dir_user_data}")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        # service=ChromeService(executable_path=os.path.join(os.getcwd(), "chromedriver.exe")),
        options=options,
    )

    stealth(
        driver,
        languages=["en-US", "en", "ru"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    log.info(
        f"create new driver: {driver}\n"
        f'navigator.webdriver: {driver.execute_script("return navigator.webdriver;")}\n'
        f'navigator.languages: {driver.execute_script("return navigator.languages;")}\n'
        f'Plugins: {driver.execute_script("return JSON.stringify(Array.from(navigator.plugins).map(p => p.name));")}\n'
        f'UA: {driver.execute_script("return navigator.userAgent;")}\n'
    )
    return driver


def make_checkin(driver):
    log.info(f"Открывает страницу {url}")
    driver.get(url)

    for _ in range(50):
        x = 7
        log.info(f"Ждем {x} сек.")
        time.sleep(x)

        try:
            log.info(f"Проверяем залогинены мы или нет")
            login_link = driver.find_element(By.CSS_SELECTOR, "[data-cm-event='login']")
            login_link.click()

            # Ожидание редиректа
            y = 5
            log.info(f"Ждем {y} сек.")
            time.sleep(y)

            # Заполнение логина и пароля
            log.info(f"Изщем поля логин и пароль")
            login_field = driver.find_element(By.ID, "id_login")
            password_field = driver.find_element(By.ID, "id_password")

            log.info(f"Очистка полей логин и пароль перед заполнением")
            login_field.send_keys(Keys.CONTROL + "a")
            login_field.send_keys(Keys.DELETE)

            password_field.send_keys(Keys.CONTROL + "a")
            password_field.send_keys(Keys.DELETE)

            log.info(f"Заполняем логин и пароль")
            login_field.send_keys(LOGIN)
            password_field.send_keys(PASSWORD)

            log.info(f"Ставим галочку 'Запомнить меня'")
            remember_checkbox = driver.find_element(By.CSS_SELECTOR, "[for='id_remember']")
            remember_checkbox.click()

            log.info(f"Нажатие на кнопку 'Войти'")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button.button-airy")
            submit_button.click()

            # Ожидание для наблюдения результатов
            n = 10
            log.info(f"Ждем {n} сек.")
            time.sleep(n)
        except NoSuchElementException:
            pass

        try:
            log.info(f"Ищем и нажимаем на награду который надо получить")
            first_element = driver.find_element(By.CSS_SELECTOR, ".c_item.c_default")
            first_element.click()

            k = 5
            log.info(f"Ждем {k} сек.")
            time.sleep(k)

            log.info(f"Извлекаем данные из полученной награды")
            task_block = driver.find_element(By.CSS_SELECTOR, ".c_task__body.c_task__comlete")
            title = task_block.find_element(By.CSS_SELECTOR, ".c_task__title").text
            sub_title = task_block.find_element(By.CSS_SELECTOR, ".c_task__sub-title").text
            reward_text = task_block.find_element(By.CSS_SELECTOR, ".c_task__text p").text

            log.info(f"Заголовок: {title}")
            log.info(f"Подзаголовок: {sub_title}")
            log.info(f"Текст награды: {reward_text}")
            log.info(f"Завершаем скрипт")
            return
        except NoSuchElementException:
            log.info("Вероятно отметка уже получена или не прогрузилась страница проверяем")

        try:
            # Есть галочки
            driver.find_element(By.CSS_SELECTOR, ".c_item.c_comlete")
            log.info("Найдены полученные отметки")
            # Есть неактивные отметки
            driver.find_element(By.CSS_SELECTOR, ".c_item.c_desable")
            log.info("Найдена отметка которую надо получить завтра")
            log.info("Отмета уже получена, завершаем работу")
            driver.close()
            sys.exit()
        except NoSuchElementException:
            log.info("Проверка на наличие уже полученной отметки не удалась, обновляем страницу")
            driver.refresh()
    return


RUN_IN_BACKGROUND = 1
url = "https://tanki.su/ru/daily-check-in/"

if __name__ == "__main__":
    log.info("Запуск драйвера")
    if not RUN_IN_BACKGROUND:
        driver = driver_init(headless=0)
        # Переход на страницу с элементами
        driver.get(url)
    else:
        driver = driver_init(headless=1)
        # driver = driver_init(headless=0)

    log.info("Начало работы")
    make_checkin(driver)
    driver.close()

    # s = 12 * 60 * 60
    # log.info(f"Спим {s / 60 / 60} часа")
    # time.sleep(s)

    # log.info("Выход")
    # sys.exit()
