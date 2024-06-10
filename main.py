from config import load_settings, load_coins_settings, update_coins_settings
from coinbase import get_accounts, get_current_price
from trading import check_price_trends
import threading
import time

def main():
    settings = load_settings()
    accounts = get_accounts()

    # Load existing coins settings if they exist to preserve existing data
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

        # Update the network settings with the current data
        if network not in coins_settings:
            coins_settings[network] = {
                'enabled': False,
                'current_price': current_price if current_price is not None else "N/A",
                'current_cost_usd': -1,
                'usd_value': usd_value if usd_value is not None else "N/A",
                'balance': balance,
                'price_trends': [],
                'trend_status': None
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

    # Load existing coins_settings to preserve 'current_cost_usd', 'price_trends', and 'enabled'
    existing_coins_settings = load_coins_settings()
    for network in existing_coins_settings:
        if 'current_cost_usd' in existing_coins_settings[network]:
            coins_settings[network]['current_cost_usd'] = existing_coins_settings[network]['current_cost_usd']
        if 'enabled' in existing_coins_settings[network]:
            coins_settings[network]['enabled'] = existing_coins_settings[network]['enabled']
        if 'price_trends' in existing_coins_settings[network]:
            coins_settings[network]['price_trends'] = existing_coins_settings[network]['price_trends']
        if 'trend_status' in existing_coins_settings[network]:
            coins_settings[network]['trend_status'] = existing_coins_settings[network]['trend_status']

    update_coins_settings(coins_settings)

    # Start a thread to check price trends at the specified interval
    refresh_interval = settings.get('refresh_interval', 60)

    def run_price_trends():
        while True:
            check_price_trends()
            time.sleep(refresh_interval)

    price_trends_thread = threading.Thread(target=run_price_trends)
    price_trends_thread.daemon = True
    price_trends_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
