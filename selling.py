from coinbase import get_current_price, place_market_order
from config import load_coins_settings, update_coins_settings

def sell_coin(coin):
    settings = load_coins_settings()
    coin_settings = settings[coin]
    balance = coin_settings['balance']
    current_price = coin_settings['current_price']

    if current_price == "N/A" or balance <= 0:
        print(f"Cannot sell {coin}. No valid price or balance.")
        return

    base_size = balance

    success, order_id, error = place_market_order(f"{coin}-USD", 'SELL', base_order_size=base_size)
    if success:
        print(f"Sell order placed successfully for {coin}, order ID: {order_id}")
        coin_settings['balance'] = 0
        coin_settings['usd_value'] = 0
        coin_settings['current_cost_usd'] = -1  # Reset cost after selling
    else:
        print(f"Failed to place sell order for {coin}: {error}")

    update_coins_settings(settings)

def check_sell_opportunities():
    settings = load_coins_settings()
    for coin, coin_settings in settings.items():
        if coin_settings['enabled'] and coin_settings['current_price'] != "N/A":
            sell_coin(coin)
