from coinbase import place_market_order
from config import load_coins_settings, update_coins_settings

def sell_coin(coin):
    coins_settings = load_coins_settings()
    base_size = coins_settings[coin]['balance']

    if base_size > 0:
        print(f"Selling {coin}: Testing sale with unknown cost.")
        success, order_id, error = place_market_order(f"{coin}-USD", 'SELL', size=base_size)

        if success:
            print(f"Sell order placed successfully for {coin}, order ID: {order_id}")
            # Update the coin settings after a successful sale
            coins_settings[coin]['balance'] -= base_size
            coins_settings[coin]['current_cost_usd'] = -1  # Reset cost after sale
            update_coins_settings(coins_settings)
        else:
            print(f"Failed to place sell order for {coin}: {error}")

def check_sell_opportunities():
    coins_settings = load_coins_settings()

    for coin, settings in coins_settings.items():
        if settings['enabled']:
            trend_status = settings.get('trend_status', 'none')
            current_price = settings['current_price']
            current_cost = settings['current_cost_usd']
            balance = settings['balance']

            if trend_status == 'upward' and current_cost != -1:
                profit_margin = ((current_price - current_cost) / current_cost) * 100
                if profit_margin >= settings.get('sale_threshold', 10):
                    sell_coin(coin)
            elif current_cost == -1:
                sell_coin(coin)
