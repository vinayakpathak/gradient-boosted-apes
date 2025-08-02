#!/usr/bin/env python3
"""
Print current bid/ask spreads for every perp on
  • dYdX v4 main-net indexer
  • Hyperliquid main-net info endpoint

Dependencies:  requests (pip install requests)
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures as cf
from typing import Dict, Tuple

# -------- dYdX helpers -------------------------------------------------------
DYDX_BASE = "https://indexer.dydx.trade/v4"

def _dydx_orderbook(ticker: str) -> float:
    """Return best-bid, best-ask for one dYdX perp (or None, None on error)."""
    url = f"{DYDX_BASE}/orderbooks/perpetualMarket/{ticker}"
    try:
        ob = requests.get(url, timeout=4).json()
        best_bid = float(ob["bids"][0]["price"])
        best_ask = float(ob["asks"][0]["price"])
        return best_bid, best_ask
    except Exception:
        return None, None

def dydx_spreads() -> dict[str, float]:
    """Map ticker → spread percentage ((ask-bid)/mid)."""
    markets = requests.get(f"{DYDX_BASE}/perpetualMarkets", timeout=4).json()["markets"]  # :contentReference[oaicite:0]{index=0}
    tickers = [m["ticker"] for m in markets.values()]
    spreads = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_dydx_orderbook, t): t for t in tickers}
        for f in as_completed(futures):
            tkr = futures[f]
            bid, ask = f.result()
            if bid is not None and ask is not None:
                mid = (ask + bid) / 2
                spreads[tkr] = (ask - bid) / mid
    return spreads


# -------- Hyperliquid helpers ------------------------------------------------
HL_BASE = "https://api.hyperliquid.xyz/info"
HEADERS  = {
    "Content-Type": "application/json",
    "User-Agent"  : "spread-checker/0.1 (+https://github.com/you)"
}
def hl_universe() -> list[str]:
    r = requests.post(HL_BASE, json={"type": "meta"}, headers=HEADERS, timeout=7)
    r.raise_for_status()
    meta = r.json()                                   # returns {"universe": [...], ...}
    coins = [
        c["name"] for c in meta["universe"]
        if not c.get("isDelisted", False)
    ]                                                # docs: meta ⇒ universe field:contentReference[oaicite:0]{index=0}
    return coins

# 2️⃣ grab level-2 snapshot for one coin
def hl_best_bid_ask(coin: str) -> Tuple[float, float] | None:
    payload = {"type": "l2Book", "coin": coin}
    try:
        r = requests.post(HL_BASE, json=payload, headers=HEADERS, timeout=7)
        r.raise_for_status()
        data = r.json()
        # The API returns {"coin": "...", "time": ..., "levels": [bids, asks]}
        bids, asks = data["levels"]                        # Extract bids and asks from levels field
        return float(bids[0]["px"]), float(asks[0]["px"])
    except Exception as e:
        return None

def hl_spreads() -> Dict[str, float]:
    spreads = {}
    coins = hl_universe()
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for coin, res in zip(coins, pool.map(hl_best_bid_ask, coins)):
            if res:
                bid, ask = res
                mid = (ask + bid) / 2
                spreads[coin] = (ask - bid) / mid
    return spreads


# ------------------------------ main -----------------------------------------
def find_common_pairs_and_sort():
    """Find pairs traded on both exchanges and sort by spread difference (decreasing)"""
    print("Fetching dYdX spreads...")
    dydx_data = dydx_spreads()
    print("Fetching Hyperliquid spreads...")
    hl_data = hl_spreads()
    
    # Normalize dYdX pairs by removing "-USD" suffix
    dydx_normalized = {}
    for pair, spread in dydx_data.items():
        if pair.endswith("-USD"):
            normalized = pair[:-4]  # Remove "-USD"
            dydx_normalized[normalized] = spread
    
    # Find common pairs (case-insensitive matching)
    dydx_lower = {k.lower(): v for k, v in dydx_normalized.items()}
    hl_lower = {k.lower(): v for k, v in hl_data.items()}
    
    common_pairs = []
    for dydx_pair, dydx_spread in dydx_normalized.items():
        hl_pair = None
        # Try exact match first
        if dydx_pair in hl_data:
            hl_pair = dydx_pair
        # Try case-insensitive match
        elif dydx_pair.lower() in hl_lower:
            # Find the original case version
            for k, v in hl_data.items():
                if k.lower() == dydx_pair.lower():
                    hl_pair = k
                    break
        
        if hl_pair:
            hl_spread = hl_data[hl_pair]
            # Calculate difference (dYdX spread - Hyperliquid spread)
            spread_diff = dydx_spread - hl_spread
            common_pairs.append({
                'pair': dydx_pair,
                'dydx_spread': dydx_spread,
                'hl_spread': hl_spread,
                'difference': spread_diff
            })
    
    # Sort by difference in decreasing order (largest differences first)
    common_pairs.sort(key=lambda x: x['difference'], reverse=True)
    return common_pairs

if __name__ == "__main__":
    print("=== Common Pairs (sorted by spread difference, decreasing) ===")
    print("Spreads shown as percentages: (ask-bid)/mid")
    print("Difference = dYdX Spread % - Hyperliquid Spread %")
    print("Positive difference = dYdX has wider spreads")
    print("Negative difference = Hyperliquid has wider spreads")
    print("Pair        dYdX Spread%  HL Spread%   Difference")
    print("-" * 55)
    
    common_pairs = find_common_pairs_and_sort()
    
    for pair_info in common_pairs:
        diff_str = f"{pair_info['difference']:+.8f}"  # Show sign
        print(f"{pair_info['pair']:<10} {pair_info['dydx_spread']:.8f}   {pair_info['hl_spread']:.8f}   {diff_str}")
    
    print(f"\nFound {len(common_pairs)} common pairs")
