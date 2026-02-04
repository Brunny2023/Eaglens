import os

# Telegram Bot Token (to be provided by user)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8412034421:AAHsfCrH00KDe7iTKhyFXdmdPkoLA8SoY-g")

# Football-Data.org API Key (to be provided by user)
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "b2d4e4fd5ed54f6b967fd6c40f2c6635")

# Gating Thresholds
BRIER_THRESHOLD = 0.23
PERFORMANCE_DRIFT_SUPPRESS = 0.25
DATA_DRIFT_PSI_SUPPRESS = 0.40
LEAGUE_VOLATILITY_SUPPRESS = 1.50
MIN_SAMPLE_SIZE = 5

# Confidence Labels
CONFIDENCE_HIGH = (70, 100)
CONFIDENCE_MEDIUM = (45, 69)
CONFIDENCE_LOW = (0, 44)

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "eaglens.db")

# Paystack Configuration
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "YOUR_PAYSTACK_SECRET_KEY")
PAYSTACK_TRIAL_PRICE = 7.99
PAYSTACK_QUARTERLY_PRICE = 19.99
PAYSTACK_MONTHLY_PRICE = 349.00
PAYSTACK_CURRENCY = "USD"

# Owner Configuration
OWNER_USERNAME = "@lordsgreat"
OWNER_ID = 0  # Will be updated once the owner interacts with the bot
