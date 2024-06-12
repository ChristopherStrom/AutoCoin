from config import load_coins_settings, update_coins_settings, load_settings
from coinbase import get_current_price
import time


def check_price_trends():
    while True:
        coins_settings = load_coins_settings()
        for coin, settings in coins_settings.items():
            if settings['enabled']:
                product_id = f"{coin}-USD"
                current_price = get_current_price(product_id)

                if current_price is not None:
                    previous_price = settings.get('previous_price', current_price)

                    if previous_price == 0:
                        print(f"Previous price for {coin} is zero. Skipping trend calculation.")
                        settings['previous_price'] = current_price
                        continue

                    price_change = (current_price - previous_price) / previous_price

                    if len(settings['price_trends']) >= 10:
                        settings['price_trends'].pop(0)
                    settings['price_trends'].append(price_change)

                    if price_change > 0:
                        trend_status = 'upward'
                    elif price_change < 0:
                        trend_status = 'downward'
                    else:
                        trend_status = 'stable'

                    settings['trend_status'] = trend_status
                    settings['previous_price'] = current_price

                    print(f"Checking {coin}:")
                    print(f"  Previous Price: {previous_price}")
                    print(f"  Current Price: {current_price}")
                    print(f"  Price Change: {price_change}")
                    print(f"  Trend Status: {trend_status}\n")

        update_coins_settings(coins_settings)
        time.sleep(load_settings()['refresh_interval'])
