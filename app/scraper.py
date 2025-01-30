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
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class BrowserFactory:
    @staticmethod
    def validate_heroku_environment():
        if Config.IS_HEROKU:
            logger.info("Validating Heroku environment...")
            # Validate Chrome binary
            if not os.path.exists(Config.CHROME_BINARY_PATH):
                raise RuntimeError(f"Chrome binary not found at {Config.CHROME_BINARY_PATH}")
            logger.info(f"Chrome binary found at {Config.CHROME_BINARY_PATH}")
            
            # Validate ChromeDriver
            if not os.path.exists(Config.CHROME_DRIVER_PATH):
                raise RuntimeError(f"ChromeDriver not found at {Config.CHROME_DRIVER_PATH}")
            logger.info(f"ChromeDriver found at {Config.CHROME_DRIVER_PATH}")
            
            # Log system information
            logger.info("Heroku environment details:")
            logger.info(f"OS: {platform.system()} {platform.version()}")
            logger.info(f"Python version: {sys.version}")
            logger.info(f"Working directory: {os.getcwd()}")
            logger.info(f"Directory contents: {os.listdir('.')}")

    @staticmethod
    def create_driver(browser_type):
        try:
            # Validate environment first
            BrowserFactory.validate_heroku_environment()
            
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
                    logger.info(f"Chrome binary path: {Config.CHROME_BINARY_PATH}")
                    logger.info(f"Chrome driver path: {Config.CHROME_DRIVER_PATH}")
                    
                    # Test file permissions
                    logger.info(f"Chrome binary permissions: {oct(os.stat(Config.CHROME_BINARY_PATH).st_mode)[-3:]}")
                    logger.info(f"ChromeDriver permissions: {oct(os.stat(Config.CHROME_DRIVER_PATH).st_mode)[-3:]}")
                    
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
                    # Verify driver is working
                    driver.get("about:blank")
                    logger.info("Driver successfully loaded blank page")
                    return driver
                except Exception as e:
                    logger.error("Chrome driver creation failed")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Error message: {str(e)}")
                    logger.error(f"Stack trace: {traceback.format_exc()}")
                    raise

            else:
                raise ValueError("Only Chrome browser is supported") 
                
        except Exception as e:
            logging.error(f"Driver creation failed: {str(e)}")
            raise

    @staticmethod
    def setup_chrome():
        logging.info("Setting up ChromeDriver")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            from sys import platform
            if platform == "darwin":  # macOS
                # Use ChromeDriver Manager with specific settings for macOS
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                from webdriver_manager.core.os_manager import ChromeType
                
                service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Default setup for other platforms
                driver = webdriver.Chrome(options=options)
            
            return driver
        except Exception as e:
            logging.error(f"Chrome driver error: {str(e)}")
            logging.error(f"Platform: {platform}")
            raise

class UAFScraper:
    def __init__(self):
        self.browser_type = Config.BROWSER_TYPE
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def get_result_html(self, reg_number):
        last_exception = None
        for attempt in range(self.max_retries):
            driver = None
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to scrape results for reg number: {reg_number}")
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

                logger.info("Waiting for submit button...")
                submit_button = WebDriverWait(driver, Config.CHROME_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'][@value='Result']"))
                )

                logger.info("Clicking submit button...")
                submit_button.click()

                # Wait for result content to load
                WebDriverWait(driver, Config.CHROME_TIMEOUT).until(
                    lambda d: len(d.page_source) > 500  # Basic check for content load
                )

                page_source = driver.page_source
                if "Result Not Found" in page_source or len(page_source.strip()) < 500:
                    raise ValueError("No valid result content found")

                logger.info("Successfully retrieved page source")
                return page_source

            except TimeoutException as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt + 1}: {str(e)}")
            except WebDriverException as e:
                last_exception = e
                logger.warning(f"WebDriver error on attempt {attempt + 1}: {str(e)}")
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
            finally:
                if driver:
                    try:
                        driver.quit()
                        logger.info("Driver closed successfully")
                    except Exception as e:
                        logger.error(f"Error closing driver: {str(e)}")

            if attempt < self.max_retries - 1:
                import time
                time.sleep(self.retry_delay)

        raise last_exception or Exception("Failed to fetch result after all retries")
