import random
import time
import datetime
import logging

# Setup logging to file for trade records.
def setup_logger():
    logger = logging.getLogger("TradeLogger")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("trading_log.txt")
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = setup_logger()

# Initial trading parameters
initial_capital = 1000.0
usd_balance = initial_capital
xrp_balance = 0.0
trade_history = []  # List to store trade details

# Function to simulate buying XRP.
def buy_xrp(amount_usd, price, venue):
    global usd_balance, xrp_balance
    if amount_usd > usd_balance:
        print("Insufficient USD balance to buy.")
        return
    xrp_bought = amount_usd / price
    usd_balance -= amount_usd
    xrp_balance += xrp_bought
    trade_details = {
        "time": datetime.datetime.now(),
        "action": "BUY",
        "venue": venue,
        "price": price,
        "usd_spent": amount_usd,
        "xrp_received": xrp_bought
    }
    trade_history.append(trade_details)
    logger.info(f"BUY on {venue}: Price={price:.4f}, USD={amount_usd:.2f}, XRP={xrp_bought:.4f}")
    print(f"Executed BUY: {trade_details}")

# Function to simulate selling XRP.
def sell_xrp(amount_xrp, price, venue):
    global usd_balance, xrp_balance
    if amount_xrp > xrp_balance:
        print("Insufficient XRP balance to sell.")
        return
    usd_received = amount_xrp * price
    xrp_balance -= amount_xrp
    usd_balance += usd_received
    trade_details = {
        "time": datetime.datetime.now(),
        "action": "SELL",
        "venue": venue,
        "price": price,
        "usd_received": usd_received,
        "xrp_sold": amount_xrp
    }
    trade_history.append(trade_details)
    logger.info(f"SELL on {venue}: Price={price:.4f}, XRP={amount_xrp:.4f}, USD={usd_received:.2f}")
    print(f"Executed SELL: {trade_details}")

# Function to simulate fetching the market price with random volatility.
def simulate_market_price(base=0.5, volatility=0.05):
    return round(random.uniform(base - volatility, base + volatility), 4)

def main():
    global usd_balance, xrp_balance
    # Define simulation trading window (e.g., 30 seconds for demo purposes).
    trading_start = datetime.datetime.now()
    trading_end = trading_start + datetime.timedelta(seconds=30)
    print(f"Trading simulation started at {trading_start.strftime('%H:%M:%S')}")
    print(f"Trading will end at {trading_end.strftime('%H:%M:%S')}")

    # Define mispricing threshold (e.g., 1% difference).
    threshold = 0.01  # 1%

    try:
        while datetime.datetime.now() < trading_end:
            # Simulate fetching market data from two venues.
            price_venue1 = simulate_market_price()
            price_venue2 = simulate_market_price()

            print(f"Venue1 Price: ${price_venue1}, Venue2 Price: ${price_venue2}")

            # Check for arbitrage opportunity: Buy low and sell high.
            if price_venue1 < price_venue2 and (price_venue2 - price_venue1) / price_venue1 >= threshold:
                trade_amount = usd_balance * 0.10  # Use 10% of available capital.
                print("Arbitrage Opportunity: Buy on Venue1 and Sell on Venue2")
                buy_xrp(trade_amount, price_venue1, "Venue1")
                time.sleep(0.5)  # Simulate slight delay in execution.
                xrp_to_sell = trade_amount / price_venue1  # Sell all XRP bought.
                sell_xrp(xrp_to_sell, price_venue2, "Venue2")
            elif price_venue2 < price_venue1 and (price_venue1 - price_venue2) / price_venue2 >= threshold:
                trade_amount = usd_balance * 0.10
                print("Arbitrage Opportunity: Buy on Venue2 and Sell on Venue1")
                buy_xrp(trade_amount, price_venue2, "Venue2")
                time.sleep(0.5)
                xrp_to_sell = trade_amount / price_venue2
                sell_xrp(xrp_to_sell, price_venue1, "Venue1")
            else:
                print("No arbitrage opportunity detected.")

            time.sleep(1)  # Wait before next iteration.
    except Exception as e:
        print("An error occurred during trading:", e)
    finally:
        print("\nTrading simulation ended.")
        print(f"Final USD Balance: ${usd_balance:.2f}")
        print(f"Final XRP Balance: {xrp_balance:.4f}")
        pnl = usd_balance - initial_capital
        print(f"Profit/Loss: ${pnl:.2f}")
        print("\nTrade History:")
        for trade in trade_history:
            print(trade)

if __name__ == "__main__":
    main()
