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
        DRIVER_CACHE_PATH = os.path.join(
            os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "ChromeDriver"
        )
    else:
        CHROME_BINARY_PATH = os.getenv("GOOGLE_CHROME_BIN", "/app/.apt/usr/bin/google-chrome")
        CHROME_DRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/app/.chromedriver/bin/chromedriver")
        DRIVER_CACHE_PATH = "/tmp/webdriver"

    # Browser settings
    BROWSER_TYPE = "chrome"
