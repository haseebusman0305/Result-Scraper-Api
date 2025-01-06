from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
import logging
import os
import sys
import platform

class BrowserFactory:
    @staticmethod
    def create_driver(browser_type):
        try:
            os.makedirs(Config.DRIVER_CACHE_PATH, exist_ok=True)

            if browser_type == "chrome":
                options = ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--remote-debugging-port=9222")

                if Config.IS_HEROKU:
                    options.binary_location = Config.CHROME_BINARY_PATH
                driver_path = ChromeDriverManager().install()
                service = ChromeService(executable_path=driver_path)

                logging.info(f"Chrome binary location: {options.binary_location}")
                logging.info(f"ChromeDriver path: {service.path}")

                try:
                    driver = webdriver.Chrome(
                        service=service,
                        options=options
                    )
                    return driver
                except Exception as e:
                    logging.error(f"Chrome driver error: {str(e)}")
                    raise

            else:
                raise ValueError("Only Chrome browser is supported") 
                
        except Exception as e:
            logging.error(f"Driver creation failed: {str(e)}")
            raise

class UAFScraper:
    def __init__(self):
        self.browser_type = Config.BROWSER_TYPE

    def get_result_html(self, reg_number):
        driver = None
        try:
            driver = BrowserFactory.create_driver(self.browser_type)
            driver.set_page_load_timeout(Config.CHROME_TIMEOUT)
            driver.set_script_timeout(Config.CHROME_TIMEOUT)

            driver.get("http://lms.uaf.edu.pk/login/index.php")

            reg_input = WebDriverWait(driver, Config.CHROME_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "REG"))
            )
            reg_input.send_keys(reg_number)

            submit_button = driver.find_element(
                By.XPATH, "//input[@type='submit'][@value='Result']"
            )
            submit_button.click()

            return driver.page_source

        except Exception as e:
            logging.error(f"Scraping error: {str(e)}")
            raise
        finally:
            if driver:
                driver.quit()

