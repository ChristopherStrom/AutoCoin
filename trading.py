import time
from config import load_coins_settings, update_coins_settings, load_trends, save_trends, load_settings
from coinbase import get_current_price
from selling import check_sell_opportunities
from buying import check_buy_opportunities

def check_price_trends():
    while True:
        coins_settings = load_coins_settings()

        for coin, settings in coins_settings.items():
            if settings['enabled']:
                current_price = get_current_price(f"{coin}-USD")
                previous_price = settings['previous_price']
                price_trends = load_trends(coin)

                if previous_price:
                    price_change = (current_price - previous_price) / previous_price
                    price_trends.append(price_change)
                    price_trends = price_trends[-10:]  # Keep only the last 10 trends

                    trend_status = "upward" if price_change > 0 else "downward"
                    coins_settings[coin]['trend_status'] = trend_status

                save_trends(coin, price_trends)
                settings['previous_price'] = current_price

        update_coins_settings(coins_settings)
        check_sell_opportunities()
        check_buy_opportunities()
        time.sleep(load_settings()['refresh_interval'])
