from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import random
import time
from datetime import datetime


# Definíciós rész
SCREENSHOTS_DIR = "./badScreenshots/"
RESOLUTIONS = {
    "desktop": (1920, 1080),
    "laptop": (1366, 768),
    "tablet": (1536, 2048),
    "mobile": (375, 667),
}
PAGES = [
    "https://bwpool.azurewebsites.net/",
    "https://bwpool.azurewebsites.net/Customer",
    "https://bwpool.azurewebsites.net/Location",
    "https://bwpool.azurewebsites.net/Tool"
]


def execute_with_retry(action, max_retries=3):
    for _ in range(max_retries):
        try:
            return action()
        except StaleElementReferenceException:
            pass
    raise StaleElementReferenceException("Element is stale after multiple retries.")


def random_css_modification(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, 'div, span, a, img, p, h1, h2, h3, h4, h5, h6, tr, td')
    win_height = driver.execute_script("return window.innerHeight")
    win_y_offset = driver.execute_script("return window.pageYOffset")

    screen_elements_info = []
    for el in elements:
        if el.is_displayed():
            el_loc = el.location
            if el_loc['y'] >= win_y_offset and el_loc['y'] <= (win_y_offset + win_height):
                screen_elements_info.append({"element": el, "location": el_loc})

    if not screen_elements_info:
        return

    target_info = random.choice(screen_elements_info)
    target_element = target_info["element"]

    action = execute_with_retry(lambda: random.choice(['hide', 'move', 'style', 'add']))

    if action == 'hide':
        driver.execute_script("arguments[0].style.display = 'none';", target_element)
    elif action == 'move':
        margin_value = f"{random.randint(10, 50)}px"
        driver.execute_script(f"arguments[0].style.marginTop = '{margin_value}';", target_element)
    elif action == 'style':
        color_value = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
        driver.execute_script(f"arguments[0].style.color = '{color_value}';", target_element)
    elif action == 'add':
        width_value = f"{random.randint(10, 200)}px"
        height_value = f"{random.randint(10, 200)}px"
        bg_color_value = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
        new_element = f'<div style="width: {width_value}; height: {height_value}; background-color: {bg_color_value}"></div>'
        driver.execute_script(f"arguments[0].insertAdjacentHTML('beforeend', '{new_element}');", target_element)


def unique_screenshot_name(device, page_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = ''.join(random.choices('0123456789ABCDEF', k=4))
    return f"{SCREENSHOTS_DIR}{device}_{page_name}_{timestamp}_{random_str}.png"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")

browsers = {
    "chrome": webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=chrome_options),
    "firefox": webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=firefox_options)
}

num_runs = 4

for browser_name, driver in browsers.items():
    for _ in range(num_runs):
        for device, resolution in RESOLUTIONS.items():
            width, height = resolution
            driver.set_window_size(width, height)
            
            for page in PAGES:
                driver.get(page)
                time.sleep(3)
                
                num_modifications = random.randint(1, 10)
                for _ in range(num_modifications):
                    random_css_modification(driver)
                
                screenshot_path = unique_screenshot_name(f"{browser_name}_{device}", page.split('/')[-1])
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")

                add_buttons = driver.find_elements(By.XPATH, "//*[@id='Grid_add']/button")
                time.sleep(1)
                if add_buttons:
                    driver.execute_script("arguments[0].click();", add_buttons[0])
                    time.sleep(3)
                    
                    screenshot_path = unique_screenshot_name(f"{browser_name}_{device}", page.split('/')[-1] + "_add")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")

    driver.quit()
