"""
Configuration file for the arbitrage trading bot
"""

# Trading Configuration
TRADING_PAIR = "BRETT"
TRADE_SIZE = 1.0  # Size of each trade in units
PRICE_UPDATE_THRESHOLD = 0.001  # 0.1% threshold for updating orders

# API Configuration
DYDX_CONFIG = {
    "api_key": "your_dydx_api_key",
    "api_secret": "your_dydx_api_secret", 
    "passphrase": "your_dydx_passphrase"
}

HYPERLIQUID_CONFIG = {
    "api_key": "your_hl_api_key",
    "api_secret": "your_hl_api_secret"
}

# Pricing Algorithm Configuration
PRICING_ALGORITHM = "best_bid_ask"  # Options: "best_bid_ask", "mid_price_offset"

# Risk Management
MAX_POSITION_SIZE = 10.0  # Maximum position size
MAX_DAILY_TRADES = 100   # Maximum trades per day
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "arbitrage_trader.log"

# Trading Loop Configuration
LOOP_INTERVAL = 1.0  # Seconds between trading loop iterations
ERROR_RETRY_DELAY = 5.0  # Seconds to wait after an error 