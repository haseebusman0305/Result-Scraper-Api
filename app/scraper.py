from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from config import Config
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import logging
import os
import sys
import platform
import traceback
import glob

logger = logging.getLogger(__name__)

class BrowserFactory:
    @staticmethod
    def create_driver(browser_type):
        try:
            os.makedirs(Config.DRIVER_CACHE_PATH, exist_ok=True)

            if browser_type == "chrome":
                options = ChromeOptions()
                # Common options for both platforms
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                if Config.IS_HEROKU:
                    logger.info("Setting up Chrome for Heroku")
                    options.binary_location = Config.CHROME_BINARY_PATH
                    service = ChromeService(executable_path=Config.CHROME_DRIVER_PATH)
                else:
                    logger.info(f"Setting up ChromeDriver for Windows")
                    driver_path = ChromeDriverManager().install()
                    
                    # Handle Windows-specific path issues
                    if Config.IS_WINDOWS:
                        driver_dir = os.path.dirname(driver_path)
                        chromedriver_pattern = 'chromedriver.exe' if Config.IS_WINDOWS else 'chromedriver'
                        chromedriver_path = next(
                            (f for f in glob.glob(f"{driver_dir}/**/{chromedriver_pattern}", recursive=True)),
                            None
                        )
                        if chromedriver_path:
                            driver_path = chromedriver_path
                            logger.info(f"Found ChromeDriver at: {driver_path}")
                    
                    service = ChromeService(executable_path=driver_path)

                try:
                    driver = webdriver.Chrome(service=service, options=options)
                    logger.info("Chrome driver created successfully")
                    return driver
                except Exception as e:
                    logger.error(f"Chrome driver error: {str(e)}")
                    logger.error(f"Platform: {platform.system()}")
                    logger.error(f"Chrome binary exists: {os.path.exists(Config.CHROME_BINARY_PATH)}")
                    logger.error(f"Chrome driver exists: {os.path.exists(driver_path)}")
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
            logger.info(f"Attempting to scrape results for reg number: {reg_number}")
            driver = BrowserFactory.create_driver(self.browser_type)
            driver.set_page_load_timeout(Config.CHROME_TIMEOUT)
            driver.set_script_timeout(Config.CHROME_TIMEOUT)

            logger.info("Loading URL...")
            driver.get("http://lms.uaf.edu.pk/login/index.php")

            logger.info("Waiting for input field...")
            reg_input = WebDriverWait(driver, Config.CHROME_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "REG"))
            )

            logger.info("Entering registration number...")
            reg_input.send_keys(reg_number)

            logger.info("Clicking submit button...")
            submit_button = driver.find_element(
                By.XPATH, "//input[@type='submit'][@value='Result']"
            )
            submit_button.click()

            logger.info("Successfully retrieved page source")
            return driver.page_source

        except Exception as e:
            logger.error(f"Scraping error for reg number {reg_number}: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"System info: {sys.platform}, Python: {sys.version}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Driver closed successfully")
                except Exception as e:
                    logger.error(f"Error closing driver: {str(e)}")

