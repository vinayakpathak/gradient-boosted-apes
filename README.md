# Arbitrage Trading Bot

A modular arbitrage trading bot that executes trades between dYdX and Hyperliquid, specifically designed for BRETT trading.

## Strategy Overview

The bot implements the following arbitrage strategy:

1. **dYdX Orders**: Maintains a bid and ask order on dYdX at the current best bid/ask levels
2. **Hyperliquid Hedging**: When a dYdX order fills, immediately executes the opposite market order on Hyperliquid
3. **Profit Capture**: Captures the spread difference between the two exchanges

## Features

- **Modular Pricing Algorithm**: Easy to modify pricing strategies
- **Real-time Order Management**: Automatically updates orders based on market conditions
- **Risk Management**: Configurable position limits and stop losses
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Handling**: Robust error handling with automatic retries

## Installation

1. Install required dependencies:
```bash
pip install requests asyncio websockets
```

2. Configure API credentials in `config.py`:
```python
DYDX_CONFIG = {
    "api_key": "your_actual_dydx_api_key",
    "api_secret": "your_actual_dydx_api_secret", 
    "passphrase": "your_actual_dydx_passphrase"
}

HYPERLIQUID_CONFIG = {
    "api_key": "your_actual_hl_api_key",
    "api_secret": "your_actual_hl_api_secret"
}
```

## Usage

### Basic Usage

```python
from arbitrage_trader import ArbitrageTrader, DYDXTrader, HyperliquidTrader, PricingAlgorithm
from config import DYDX_CONFIG, HYPERLIQUID_CONFIG

# Initialize traders
dydx_trader = DYDXTrader(**DYDX_CONFIG)
hl_trader = HyperliquidTrader(**HYPERLIQUID_CONFIG)

# Initialize pricing algorithm
pricing_algorithm = PricingAlgorithm("best_bid_ask")

# Initialize arbitrage trader
trader = ArbitrageTrader(
    dydx_trader=dydx_trader,
    hl_trader=hl_trader,
    pricing_algorithm=pricing_algorithm,
    trade_size=1.0
)

# Start trading
trader.start()
```

### Running the Bot

```bash
python arbitrage_trader.py
```

## Configuration

### Trading Parameters

- `TRADING_PAIR`: The trading pair (default: "BRETT")
- `TRADE_SIZE`: Size of each trade (default: 1.0)
- `PRICE_UPDATE_THRESHOLD`: Threshold for updating orders (default: 0.001)

### Pricing Algorithms

1. **best_bid_ask**: Places orders at current best bid/ask levels
2. **mid_price_offset**: Places orders at mid price with small offset

To use a different algorithm:

```python
pricing_algorithm = PricingAlgorithm("mid_price_offset")
```

### Risk Management

- `MAX_POSITION_SIZE`: Maximum position size
- `MAX_DAILY_TRADES`: Maximum trades per day
- `STOP_LOSS_PERCENTAGE`: Stop loss percentage

## Architecture

### Core Components

1. **PricingAlgorithm**: Modular class for determining bid/ask prices
2. **DYDXTrader**: Handles all dYdX trading operations
3. **HyperliquidTrader**: Handles all Hyperliquid trading operations
4. **ArbitrageTrader**: Main orchestrator that manages the trading strategy

### Trading Flow

1. **Orderbook Monitoring**: Continuously monitors orderbooks on both exchanges
2. **Price Calculation**: Uses the pricing algorithm to determine optimal bid/ask levels
3. **Order Management**: Maintains orders on dYdX at calculated levels
4. **Fill Detection**: Monitors for order fills on dYdX
5. **Hedging**: Executes opposite market orders on Hyperliquid when dYdX orders fill

## Safety Features

- **Order Validation**: Validates all orders before placement
- **Error Recovery**: Automatic retry mechanism for failed operations
- **Position Monitoring**: Tracks current positions and prevents over-exposure
- **Graceful Shutdown**: Properly cancels all orders when stopping

## Monitoring

The bot provides comprehensive logging:

- Order placement and cancellation
- Fill notifications
- Error messages and retry attempts
- Performance metrics

## Important Notes

⚠️ **DISCLAIMER**: This is a trading bot that can result in financial losses. Use at your own risk.

### Before Running

1. **Test on Testnet**: Always test on testnet first
2. **Small Position Sizes**: Start with small trade sizes
3. **Monitor Closely**: Keep the bot under close supervision
4. **Understand the Strategy**: Make sure you understand the arbitrage strategy
5. **API Limits**: Be aware of API rate limits on both exchanges

### Risk Considerations

- **Market Risk**: Spreads can change rapidly
- **Execution Risk**: Orders may not fill at expected prices
- **Technical Risk**: Network issues or API failures
- **Regulatory Risk**: Trading regulations may change

## Customization

### Adding New Pricing Algorithms

```python
class CustomPricingAlgorithm(PricingAlgorithm):
    def _custom_strategy(self, orderbook: OrderBook) -> Tuple[float, float]:
        # Your custom logic here
        return bid_price, ask_price
```

### Modifying Trading Logic

The `ArbitrageTrader` class is designed to be easily extensible. Key methods to override:

- `_update_orders()`: Customize order update logic
- `_check_filled_orders()`: Customize fill handling
- `_trading_loop()`: Customize main trading loop

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify API credentials are correct
3. Ensure sufficient balance on both exchanges
4. Check network connectivity

## License

This project is for educational purposes. Use at your own risk. 