from config import load_settings, load_coins_settings, update_coins_settings
from coinbase import get_accounts, get_current_price
from trading import check_price_trends
import threading
import time

def refresh_balances_and_prices(settings):
    accounts = get_accounts()
    coins_settings = load_coins_settings()

    for account in accounts:
        network = account['currency']
        balance = float(account['available_balance']['value'])
        product_id = f"{network}-USD"
        current_price = get_current_price(product_id)

        if network.upper() in ['USD', 'USDC']:
            current_price = 1.0

        usd_value = balance * current_price if current_price is not None else None

        if current_price is not None:
            print(f"Account: {account['name']}")
            print(f"Network: {network}")
            print(f"Balance: {balance}")
            print(f"Current Price (USD): {current_price}")
            print(f"USD Value: {usd_value}\n")
        else:
            print(f"Could not retrieve price for {network}. Skipping...\n")

        if network not in coins_settings:
            coins_settings[network] = {
                'enabled': False,
                'current_price': current_price if current_price is not None else "N/A",
                'current_cost_usd': -1,
                'usd_value': usd_value if usd_value is not None else "N/A",
                'balance': balance,
                'price_trends': [],
                'trend_status': None,
                'previous_price': current_price
            }
        else:
            coins_settings[network]['current_price'] = current_price if current_price is not None else "N/A"
            coins_settings[network]['usd_value'] = usd_value if usd_value is not None else "N/A"
            coins_settings[network]['balance'] = balance
            if 'current_cost_usd' not in coins_settings[network]:
                coins_settings[network]['current_cost_usd'] = -1
            if 'enabled' not in coins_settings[network]:
                coins_settings[network]['enabled'] = False
            if 'price_trends' not in coins_settings[network]:
                coins_settings[network]['price_trends'] = []
            if 'trend_status' not in coins_settings[network]:
                coins_settings[network]['trend_status'] = None
            if 'previous_price' not in coins_settings[network]:
                coins_settings[network]['previous_price'] = current_price

    update_coins_settings(coins_settings)

def main():
    settings = load_settings()
    refresh_balances_and_prices(settings)

    price_trends_thread = threading.Thread(target=check_price_trends)
    price_trends_thread.daemon = True
    price_trends_thread.start()

    while True:
        time.sleep(settings['refresh_interval'])
        refresh_balances_and_prices(settings)

if __name__ == "__main__":
    main()
