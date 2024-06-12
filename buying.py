from coinbase import get_current_price, place_market_order
from config import load_coins_settings, update_coins_settings

def buy_coin(coin, usd_order_size):
    current_price = get_current_price(f"{coin}-USD")
    if current_price is None:
        print(f"Could not fetch current price for {coin}. Skipping buy.")
        return

    base_size = usd_order_size / current_price

    success, order_id, error = place_market_order(f"{coin}-USD", 'BUY', usd_order_size=usd_order_size)
    if success:
        print(f"Buy order placed successfully for {coin}, order ID: {order_id}")
        coins_settings = load_coins_settings()
        coins_settings[coin]['balance'] += base_size
        coins_settings[coin]['current_cost_usd'] = current_price
        update_coins_settings(coins_settings)
    else:
        print(f"Failed to place buy order for {coin}: {error}")

def check_buy_opportunities():
    coins_settings = load_coins_settings()
    for coin, coin_settings in coins_settings.items():
        if coin_settings['enabled'] and coin_settings['current_price'] != "N/A":
            buy_coin(coin, usd_order_size=100)  # Example buy amount
