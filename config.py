import os
from dotenv import load_dotenv
import tempfile
import platform

load_dotenv()


class Config:
    # Basic settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    CHROME_TIMEOUT = int(os.getenv("CHROME_TIMEOUT", 30))

    IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
    IS_HEROKU = "DYNO" in os.environ

    if platform.system() == "Windows":
        CHROME_BINARY_PATH = ""  # Let selenium find it automatically
        CHROME_DRIVER_PATH = ""
        DRIVER_CACHE_PATH = os.path.join(
            os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "ChromeDriver"
        )
    else:
        CHROME_BINARY_PATH = "/app/.chrome-for-testing/chrome-linux64/chrome"
        CHROME_DRIVER_PATH = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
        DRIVER_CACHE_PATH = "/tmp/webdriver"

    # Browser settings
    BROWSER_TYPE = "chrome"
