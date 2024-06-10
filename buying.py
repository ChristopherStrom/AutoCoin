from coinbase import place_market_order, get_current_price
from config import load_coins_settings, update_coins_settings

coins_settings = load_coins_settings()


def buy_coin(coin, usd_order_size):
    print(f"Buying {coin}: Initiating buy operation.")
    success, order_id, error = place_market_order(f"{coin}-USD", "BUY", usd_order_size=usd_order_size)
    if success:
        print(f"Buy order placed successfully for {coin}, order ID: {order_id}")
        # Update balance after buying
        current_price = get_current_price(f"{coin}-USD")
        balance = usd_order_size / current_price
        coins_settings[coin]['balance'] += balance
        coins_settings[coin]['current_cost_usd'] = current_price
        coins_settings[coin]['usd_value'] = coins_settings[coin]['balance'] * current_price
        update_coins_settings(coins_settings)
    else:
        print(f"Failed to place buy order for {coin}: {error}")


def check_buy_opportunities():
    for coin, details in coins_settings.items():
        if details.get('enabled', False):
            # Implement your buying strategy here
            current_price = details.get('current_price')
            balance = details.get('balance', 0)
            usd_value = details.get('usd_value', 0)

            # Example buying condition: Buy if the balance is zero and price is trending down
            if balance == 0 and current_price is not None:
                print(f"Buying opportunity detected for {coin}.")
                buy_coin(coin, usd_order_size=100)  # Example buy amount

            update_coins_settings(coins_settings)
