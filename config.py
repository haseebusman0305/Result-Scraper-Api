import os
from dotenv import load_dotenv
import tempfile
import platform
import logging
import sys

load_dotenv()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log') if "DYNO" not in os.environ else logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class Config:
    # Environment settings
    IS_HEROKU = "DYNO" in os.environ
    IS_WINDOWS = platform.system() == "Windows"
    IS_64_BITS = sys.maxsize > 2**32
    
    # Server settings
    DEBUG = os.getenv("DEBUG", str(not IS_HEROKU)).lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production" if IS_HEROKU else "development")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000 if IS_HEROKU else 5000))
    
    # Browser settings
    BROWSER_TYPE = "chrome"
    CHROME_TIMEOUT = int(os.getenv("CHROME_TIMEOUT", 30))
    
    # Chrome paths and settings
    if IS_WINDOWS:
        CHROME_BINARY_PATH = ""  # Let selenium find Chrome automatically
        CHROME_DRIVER_PATH = ""  # Will be set by webdriver_manager
        DRIVER_CACHE_PATH = os.path.join(
            os.environ.get("LOCALAPPDATA", tempfile.gettempdir()),
            "ChromeDriver",
            "win64" if IS_64_BITS else "win32"
        )
    else:
        # Heroku paths
        CHROME_BINARY_PATH = "/app/.chrome-for-testing/chrome-linux64/chrome"
        CHROME_DRIVER_PATH = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
        DRIVER_CACHE_PATH = "/tmp/webdriver"
    
    # WebDriver Manager settings
    WDM_ARCHITECTURE = "64" if IS_64_BITS else "32"
    WDM_SSL_VERIFY = False
    WDM_LOCAL = True
