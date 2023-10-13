from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import random
import time
from datetime import datetime

# Definíciós rész
# Definíciós rész
SCREENSHOTS_DIR = "./goodScreenshots/"
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

def unique_screenshot_name(device, page_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = ''.join(random.choices('0123456789ABCDEF', k=4))
    return f"{SCREENSHOTS_DIR}{device}_{page_name}_{timestamp}_{random_str}.png"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")

# Böngészők indítása WebDriver Manager segítségével
browsers = {
    "chrome": webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=chrome_options),
    "firefox": webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=firefox_options)
}

# Hányszor fusson a script
num_runs = 1

for browser_name, driver in browsers.items():
    for _ in range(num_runs):
        # Végigmegyünk az összes felbontáson
        for device, resolution in RESOLUTIONS.items():
            width, height = resolution
            driver.set_window_size(width, height)
            
            # Végigmegyünk az összes oldalon
            for page in PAGES:
                driver.get(page)
                time.sleep(3)  # Várunk, hogy az oldal betöltődjön
                
                # Képernyőkép készítése és mentése
                screenshot_path = unique_screenshot_name(f"{browser_name}_{device}", page.split('/')[-1])
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")

                # "Add" gomb megnyomása, ha létezik az oldalon
                add_buttons = driver.find_elements(By.XPATH, "//*[@id='Grid_add']/button")
                time.sleep(1)
                if add_buttons:
                    driver.execute_script("arguments[0].click();", add_buttons[0])
                    time.sleep(3)  # Várunk az interakciókra
                    
                    # Képernyőkép készítése és mentése az Add utáni állapotról
                    screenshot_path = unique_screenshot_name(f"{browser_name}_{device}", page.split('/')[-1] + "_add")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")

    # Böngésző bezárása
    driver.quit()
