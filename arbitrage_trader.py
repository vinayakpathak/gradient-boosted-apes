#!/usr/bin/env python3
"""
Arbitrage Trading Bot for dYdX and Hyperliquid
Trades BRETT using the following strategy:
- Maintain bid/ask orders on dYdX at best bid/ask levels
- When dYdX order fills, immediately execute opposite market order on Hyperliquid
- Modular algorithm design for easy modification

Dependencies: requests, asyncio, websockets (pip install requests asyncio websockets)
"""

import requests
import asyncio
import websockets
import json
import time
import logging
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TRADING_PAIR = "BRETT"
DYDX_BASE = "https://indexer.dydx.trade/v4"
HL_BASE = "https://api.hyperliquid.xyz/info"
HL_TRADE_BASE = "https://api.hyperliquid.xyz/exchange"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

@dataclass
class OrderBookLevel:
    price: float
    size: float

@dataclass
class OrderBook:
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: float

class PricingAlgorithm:
    """Modular pricing algorithm for determining bid/ask levels"""
    
    def __init__(self, name: str = "best_bid_ask"):
        self.name = name
    
    def calculate_bid_ask(self, orderbook: OrderBook) -> Tuple[float, float]:
        """
        Calculate bid and ask prices based on current orderbook
        Returns: (bid_price, ask_price)
        """
        if self.name == "best_bid_ask":
            return self._best_bid_ask_strategy(orderbook)
        elif self.name == "mid_price_offset":
            return self._mid_price_offset_strategy(orderbook)
        else:
            raise ValueError(f"Unknown pricing algorithm: {self.name}")
    
    def _best_bid_ask_strategy(self, orderbook: OrderBook) -> Tuple[float, float]:
        """Simple strategy: place orders at current best bid/ask"""
        if not orderbook.bids or not orderbook.asks:
            raise ValueError("Orderbook has no bids or asks")
        
        best_bid = orderbook.bids[0].price
        best_ask = orderbook.asks[0].price
        
        return best_bid, best_ask
    
    def _mid_price_offset_strategy(self, orderbook: OrderBook) -> Tuple[float, float]:
        """Strategy: place orders at mid price with small offset"""
        if not orderbook.bids or not orderbook.asks:
            raise ValueError("Orderbook has no bids or asks")
        
        best_bid = orderbook.bids[0].price
        best_ask = orderbook.asks[0].price
        mid_price = (best_bid + best_ask) / 2
        
        # Small offset from mid price
        offset = mid_price * 0.0001  # 0.01% offset
        
        bid_price = mid_price - offset
        ask_price = mid_price + offset
        
        return bid_price, ask_price

class DYDXTrader:
    """Handles dYdX trading operations"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = "https://api.dydx.exchange"
        
    def get_orderbook(self, ticker: str) -> OrderBook:
        """Get current orderbook for a ticker"""
        url = f"{DYDX_BASE}/orderbooks/perpetualMarket/{ticker}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            bids = [OrderBookLevel(float(level["price"]), float(level["size"])) 
                   for level in data["bids"]]
            asks = [OrderBookLevel(float(level["price"]), float(level["size"])) 
                   for level in data["asks"]]
            
            return OrderBook(bids, asks, time.time())
        except Exception as e:
            logger.error(f"Error getting dYdX orderbook: {e}")
            raise
    
    def place_order(self, ticker: str, side: OrderSide, order_type: OrderType, 
                   size: float, price: Optional[float] = None) -> Dict:
        """Place an order on dYdX"""
        # This is a placeholder - actual implementation would require dYdX API integration
        logger.info(f"Placing {side.value} {order_type.value} order on dYdX: {ticker}, size: {size}, price: {price}")
        
        # Mock response for now
        return {
            "order_id": f"dydx_{int(time.time())}",
            "status": "PENDING",
            "side": side.value,
            "type": order_type.value,
            "size": size,
            "price": price
        }
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order on dYdX"""
        logger.info(f"Canceling dYdX order: {order_id}")
        # Mock implementation
        return True
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get status of an order"""
        # Mock implementation
        return {
            "order_id": order_id,
            "status": "FILLED",  # Mock as filled
            "filled_size": 1.0
        }

class HyperliquidTrader:
    """Handles Hyperliquid trading operations"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.hyperliquid.xyz"
        
    def get_orderbook(self, coin: str) -> OrderBook:
        """Get current orderbook for a coin"""
        url = f"{HL_BASE}"
        payload = {"type": "l2Book", "coin": coin}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            bids_data, asks_data = data["levels"]
            
            bids = [OrderBookLevel(float(level["px"]), float(level["sz"])) 
                   for level in bids_data]
            asks = [OrderBookLevel(float(level["px"]), float(level["sz"])) 
                   for level in asks_data]
            
            return OrderBook(bids, asks, time.time())
        except Exception as e:
            logger.error(f"Error getting Hyperliquid orderbook: {e}")
            raise
    
    def place_market_order(self, coin: str, side: OrderSide, size: float) -> Dict:
        """Place a market order on Hyperliquid"""
        # This is a placeholder - actual implementation would require Hyperliquid API integration
        logger.info(f"Placing {side.value} market order on Hyperliquid: {coin}, size: {size}")
        
        # Mock response for now
        return {
            "order_id": f"hl_{int(time.time())}",
            "status": "FILLED",
            "side": side.value,
            "type": "MARKET",
            "size": size,
            "coin": coin
        }

class ArbitrageTrader:
    """Main arbitrage trading class"""
    
    def __init__(self, dydx_trader: DYDXTrader, hl_trader: HyperliquidTrader, 
                 pricing_algorithm: PricingAlgorithm, trade_size: float = 1.0):
        self.dydx_trader = dydx_trader
        self.hl_trader = hl_trader
        self.pricing_algorithm = pricing_algorithm
        self.trade_size = trade_size
        
        # Track current orders
        self.current_bid_order = None
        self.current_ask_order = None
        self.is_running = False
        
    def start(self):
        """Start the arbitrage trading"""
        logger.info("Starting arbitrage trading...")
        self.is_running = True
        
        try:
            asyncio.run(self._trading_loop())
        except KeyboardInterrupt:
            logger.info("Stopping arbitrage trading...")
            self.stop()
    
    def stop(self):
        """Stop the arbitrage trading"""
        self.is_running = False
        if self.current_bid_order:
            self.dydx_trader.cancel_order(self.current_bid_order["order_id"])
        if self.current_ask_order:
            self.dydx_trader.cancel_order(self.current_ask_order["order_id"])
        logger.info("Arbitrage trading stopped")
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                # Get current orderbooks
                dydx_orderbook = self.dydx_trader.get_orderbook(f"{TRADING_PAIR}-USD")
                hl_orderbook = self.hl_trader.get_orderbook(TRADING_PAIR)
                
                # Calculate new bid/ask prices
                bid_price, ask_price = self.pricing_algorithm.calculate_bid_ask(dydx_orderbook)
                
                # Check if we need to update orders
                await self._update_orders(bid_price, ask_price)
                
                # Check for filled orders
                await self._check_filled_orders()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_orders(self, bid_price: float, ask_price: float):
        """Update dYdX orders if needed"""
        # Cancel existing orders if prices have changed significantly
        price_threshold = 0.001  # 0.1% threshold
        
        if self.current_bid_order:
            current_bid_price = self.current_bid_order.get("price")
            if abs(bid_price - current_bid_price) / current_bid_price > price_threshold:
                logger.info(f"Updating bid order: {current_bid_price} -> {bid_price}")
                self.dydx_trader.cancel_order(self.current_bid_order["order_id"])
                self.current_bid_order = None
        
        if self.current_ask_order:
            current_ask_price = self.current_ask_order.get("price")
            if abs(ask_price - current_ask_price) / current_ask_price > price_threshold:
                logger.info(f"Updating ask order: {current_ask_price} -> {ask_price}")
                self.dydx_trader.cancel_order(self.current_ask_order["order_id"])
                self.current_ask_order = None
        
        # Place new orders if needed
        if not self.current_bid_order:
            self.current_bid_order = self.dydx_trader.place_order(
                f"{TRADING_PAIR}-USD", OrderSide.BUY, OrderType.LIMIT, 
                self.trade_size, bid_price
            )
            logger.info(f"Placed bid order: {bid_price}")
        
        if not self.current_ask_order:
            self.current_ask_order = self.dydx_trader.place_order(
                f"{TRADING_PAIR}-USD", OrderSide.SELL, OrderType.LIMIT, 
                self.trade_size, ask_price
            )
            logger.info(f"Placed ask order: {ask_price}")
    
    async def _check_filled_orders(self):
        """Check if any orders have been filled and execute opposite trades"""
        if self.current_bid_order:
            status = self.dydx_trader.get_order_status(self.current_bid_order["order_id"])
            if status["status"] == "FILLED":
                logger.info("Bid order filled, executing sell on Hyperliquid")
                self.hl_trader.place_market_order(TRADING_PAIR, OrderSide.SELL, self.trade_size)
                self.current_bid_order = None
        
        if self.current_ask_order:
            status = self.dydx_trader.get_order_status(self.current_ask_order["order_id"])
            if status["status"] == "FILLED":
                logger.info("Ask order filled, executing buy on Hyperliquid")
                self.hl_trader.place_market_order(TRADING_PAIR, OrderSide.BUY, self.trade_size)
                self.current_ask_order = None

def main():
    """Main function to run the arbitrage trader"""
    try:
        # Import configuration
        from config import (
            DYDX_CONFIG, HYPERLIQUID_CONFIG, PRICING_ALGORITHM, 
            TRADE_SIZE, TRADING_PAIR, LOG_LEVEL, LOG_FILE
        )
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
        logger.info("Starting arbitrage trading bot...")
        logger.info(f"Trading pair: {TRADING_PAIR}")
        logger.info(f"Trade size: {TRADE_SIZE}")
        logger.info(f"Pricing algorithm: {PRICING_ALGORITHM}")
        
        # Initialize traders
        dydx_trader = DYDXTrader(**DYDX_CONFIG)
        hl_trader = HyperliquidTrader(**HYPERLIQUID_CONFIG)
        
        # Initialize pricing algorithm
        pricing_algorithm = PricingAlgorithm(PRICING_ALGORITHM)
        
        # Initialize arbitrage trader
        trader = ArbitrageTrader(
            dydx_trader=dydx_trader,
            hl_trader=hl_trader,
            pricing_algorithm=pricing_algorithm,
            trade_size=TRADE_SIZE
        )
        
        # Start trading
        trader.start()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping...")
        if 'trader' in locals():
            trader.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'trader' in locals():
            trader.stop()
        raise

if __name__ == "__main__":
    main() 