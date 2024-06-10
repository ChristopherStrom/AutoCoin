from coinbase import get_current_price
from config import load_coins_settings, update_coins_settings

coins_settings = load_coins_settings()


def check_price_trends():
    for coin, details in coins_settings.items():
        if details.get('enabled', False):
            previous_price = details.get('previous_price')
            current_price = get_current_price(f"{coin}-USD")
            balance = details.get('balance', 0)
            current_cost_usd = details.get('current_cost_usd', -1)
            price_trends = details.get('price_trends', [])

            if current_price is not None:
                price_change = ((current_price - previous_price) / previous_price) if previous_price else 0
                price_trends.append(price_change)
                details['previous_price'] = current_price
                details['price_trends'] = price_trends
                details['current_price'] = current_price
                details['usd_value'] = current_price * balance

                # Update trend status based on price trends
                if price_change > 0:
                    trend_status = 'upward'
                elif price_change < 0:
                    trend_status = 'downward'
                else:
                    trend_status = 'stable'

                details['trend_status'] = trend_status

                update_coins_settings(coins_settings)
            else:
                print(f"Could not retrieve current price for {coin}. Skipping...")
