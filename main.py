from config import load_settings, load_coins_settings, update_coins_settings, save_trends, load_trends, ensure_settings_file
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
        current_price = None

        # Ensure the network settings exist
        if network not in coins_settings:
            coins_settings[network] = {
                'enabled': False,
                'current_price': 1.0,
                'current_cost_usd': -1,
                'usd_value': 0.0,
                'balance': balance,
                'trend_status': None,
                'previous_price': 0.0,
                'enable_conversion': True
            }

        if coins_settings[network].get('enable_conversion', True):
            current_price = get_current_price(product_id)
            if current_price is None:
                coins_settings[network]['enable_conversion'] = False
                current_price = 1.0  # Set to 1.0 when no ticker is available
        else:
            current_price = float(coins_settings[network].get('current_price', 1.0))

        if network.upper() in ['USD', 'USDC']:
            current_price = 1.0

        usd_value = balance * current_price

        if current_price is not None:
            print(f"Account: {account['name']}")
            print(f"Network: {network}")
            print(f"Balance: {balance}")
            print(f"Current Price (USD): {current_price}")
            print(f"USD Value: {usd_value}\n")
        else:
            print(f"Could not retrieve price for {network}. Skipping...\n")

        # Update the network settings with the current data
        coins_settings[network]['current_price'] = current_price
        coins_settings[network]['usd_value'] = usd_value
        coins_settings[network]['balance'] = balance
        if 'current_cost_usd' not in coins_settings[network]:
            coins_settings[network]['current_cost_usd'] = -1
        if 'enabled' not in coins_settings[network]:
            coins_settings[network]['enabled'] = False
        if 'trend_status' not in coins_settings[network]:
            coins_settings[network]['trend_status'] = None
        if 'previous_price' not in coins_settings[network]:
            coins_settings[network]['previous_price'] = current_price
        if 'enable_conversion' not in coins_settings[network]:
            coins_settings[network]['enable_conversion'] = True

        # Load and save trends
        price_trends = load_trends(network)
        save_trends(network, price_trends)

    update_coins_settings(coins_settings)

def main():
    ensure_settings_file()
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
