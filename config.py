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

    if platform.system() == "Windows":
        CHROME_PATHS = [
            os.path.join(
                os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
        ]
        CHROME_BINARY_PATH = next(
            (path for path in CHROME_PATHS if os.path.exists(path)), ""
        )
        DRIVER_CACHE_PATH = os.path.join(
            os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "ChromeDriver"
        )
    else:
        CHROME_BINARY_PATH = os.getenv('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome')
        DRIVER_CACHE_PATH = "/tmp/webdriver"

    # Browser settings
    BROWSER_TYPE = "chrome"
