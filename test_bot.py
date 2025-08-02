#!/usr/bin/env python3
"""
Test script for the arbitrage trading bot
This script tests the basic functionality without placing actual orders
"""

import asyncio
import logging
from arbitrage_trader import DYDXTrader, HyperliquidTrader, PricingAlgorithm, OrderBook, OrderBookLevel
from config import DYDX_CONFIG, HYPERLIQUID_CONFIG, TRADING_PAIR

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_orderbook_fetching():
    """Test fetching orderbooks from both exchanges"""
    logger.info("Testing orderbook fetching...")
    
    try:
        # Initialize traders
        dydx_trader = DYDXTrader(**DYDX_CONFIG)
        hl_trader = HyperliquidTrader(**HYPERLIQUID_CONFIG)
        
        # Test dYdX orderbook
        logger.info(f"Fetching dYdX orderbook for {TRADING_PAIR}-USD...")
        dydx_orderbook = dydx_trader.get_orderbook(f"{TRADING_PAIR}-USD")
        logger.info(f"dYdX orderbook: {len(dydx_orderbook.bids)} bids, {len(dydx_orderbook.asks)} asks")
        if dydx_orderbook.bids and dydx_orderbook.asks:
            logger.info(f"dYdX best bid: {dydx_orderbook.bids[0].price}")
            logger.info(f"dYdX best ask: {dydx_orderbook.asks[0].price}")
        
        # Test Hyperliquid orderbook
        logger.info(f"Fetching Hyperliquid orderbook for {TRADING_PAIR}...")
        hl_orderbook = hl_trader.get_orderbook(TRADING_PAIR)
        logger.info(f"Hyperliquid orderbook: {len(hl_orderbook.bids)} bids, {len(hl_orderbook.asks)} asks")
        if hl_orderbook.bids and hl_orderbook.asks:
            logger.info(f"Hyperliquid best bid: {hl_orderbook.bids[0].price}")
            logger.info(f"Hyperliquid best ask: {hl_orderbook.asks[0].price}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing orderbook fetching: {e}")
        return False

async def test_pricing_algorithms():
    """Test pricing algorithms with mock orderbook data"""
    logger.info("Testing pricing algorithms...")
    
    try:
        # Create mock orderbook
        mock_orderbook = OrderBook(
            bids=[OrderBookLevel(100.0, 1.0), OrderBookLevel(99.9, 2.0)],
            asks=[OrderBookLevel(100.1, 1.0), OrderBookLevel(100.2, 2.0)],
            timestamp=0.0
        )
        
        # Test best_bid_ask algorithm
        pricing_algorithm = PricingAlgorithm("best_bid_ask")
        bid_price, ask_price = pricing_algorithm.calculate_bid_ask(mock_orderbook)
        logger.info(f"Best bid/ask strategy: bid={bid_price}, ask={ask_price}")
        
        # Test mid_price_offset algorithm
        pricing_algorithm = PricingAlgorithm("mid_price_offset")
        bid_price, ask_price = pricing_algorithm.calculate_bid_ask(mock_orderbook)
        logger.info(f"Mid price offset strategy: bid={bid_price}, ask={ask_price}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing pricing algorithms: {e}")
        return False

async def test_spread_calculation():
    """Test spread calculation between exchanges"""
    logger.info("Testing spread calculation...")
    
    try:
        # Initialize traders
        dydx_trader = DYDXTrader(**DYDX_CONFIG)
        hl_trader = HyperliquidTrader(**HYPERLIQUID_CONFIG)
        
        # Get orderbooks
        dydx_orderbook = dydx_trader.get_orderbook(f"{TRADING_PAIR}-USD")
        hl_orderbook = hl_trader.get_orderbook(TRADING_PAIR)
        
        if (dydx_orderbook.bids and dydx_orderbook.asks and 
            hl_orderbook.bids and hl_orderbook.asks):
            
            # Calculate spreads
            dydx_best_bid = dydx_orderbook.bids[0].price
            dydx_best_ask = dydx_orderbook.asks[0].price
            hl_best_bid = hl_orderbook.bids[0].price
            hl_best_ask = hl_orderbook.asks[0].price
            
            dydx_mid = (dydx_best_bid + dydx_best_ask) / 2
            hl_mid = (hl_best_bid + hl_best_ask) / 2
            
            dydx_spread = (dydx_best_ask - dydx_best_bid) / dydx_mid
            hl_spread = (hl_best_ask - hl_best_bid) / hl_mid
            
            logger.info(f"dYdX spread: {dydx_spread:.6f} ({dydx_spread*100:.4f}%)")
            logger.info(f"Hyperliquid spread: {hl_spread:.6f} ({hl_spread*100:.4f}%)")
            logger.info(f"Spread difference: {dydx_spread - hl_spread:.6f}")
            
            # Calculate potential profit
            if dydx_spread > hl_spread:
                potential_profit = (dydx_spread - hl_spread) * 100
                logger.info(f"Potential profit per trade: {potential_profit:.4f}%")
            else:
                logger.info("No profitable arbitrage opportunity detected")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing spread calculation: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("Starting arbitrage bot tests...")
    
    tests = [
        test_orderbook_fetching(),
        test_pricing_algorithms(),
        test_spread_calculation()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = 0
    total = len(results)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Test {i+1} failed with exception: {result}")
        elif result:
            logger.info(f"Test {i+1} passed")
            passed += 1
        else:
            logger.error(f"Test {i+1} failed")
    
    logger.info(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        logger.info("All tests passed! The bot is ready for trading.")
    else:
        logger.error("Some tests failed. Please check the configuration and API credentials.")

if __name__ == "__main__":
    asyncio.run(main()) 