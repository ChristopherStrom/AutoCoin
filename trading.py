from config import update_coins_settings, load_coins_settings, load_settings
from coinbase import get_current_price, place_order
import time

config = load_settings()
refresh_interval = config['refresh_interval']
transaction_fee = config['transaction_fee']
sale_threshold = config['sale_threshold']
loss_limit = config['loss_limit']


def analyze_trends(trends):
    if len(trends) < 3:
        return None
    if all(x > 0 for x in trends[-3:]):
        return "upward"
    if all(x < 0 for x in trends[-3:]):
        return "downward"
    return None


def check_price_trends():
    while True:
        coins_settings = load_coins_settings()

        for network, settings in coins_settings.items():
            if settings.get('enabled', False):
                product_id = f"{network}-USD"
                current_price = get_current_price(product_id)
                if current_price is not None:
                    previous_price = settings.get('current_price')
                    balance = settings.get('balance', 0)
                    cost_usd = settings.get('current_cost_usd', -1)

                    # Track price trends
                    if 'price_trends' not in settings:
                        settings['price_trends'] = []
                    if previous_price:
                        trend = current_price - previous_price
                        settings['price_trends'].append(trend)
                        if len(settings['price_trends']) > 10:
                            settings['price_trends'].pop(0)

                    trend_analysis = analyze_trends(settings['price_trends'])

                    if balance > 0:
                        earnings = balance * current_price * (1 - transaction_fee / 100)
                        if cost_usd != -1:
                            profit = earnings - cost_usd
                            profit_percentage = (profit / cost_usd) * 100

                            # Sell if profit percentage exceeds sale threshold
                            if profit_percentage > sale_threshold:
                                print(
                                    f"Selling {network}: Profit percentage {profit_percentage}% exceeds sale threshold {sale_threshold}%")
                                success, order_id, error = place_order(product_id, "SELL", balance)
                                if success:
                                    print(f"Sell order placed successfully for {network}, order ID: {order_id}")
                                    settings['balance'] = 0
                                else:
                                    print(f"Failed to place sell order for {network}: {error}")

                            # Sell if loss exceeds loss limit
                            loss_percentage = ((cost_usd - earnings) / cost_usd) * 100
                            if loss_percentage > loss_limit:
                                print(
                                    f"Selling {network}: Loss percentage {loss_percentage}% exceeds loss limit {loss_limit}%")
                                success, order_id, error = place_order(product_id, "SELL", balance)
                                if success:
                                    print(f"Sell order placed successfully for {network}, order ID: {order_id}")
                                    settings['balance'] = 0
                                else:
                                    print(f"Failed to place sell order for {network}: {error}")

                    # Buy if trending upward after a downward trend
                    if trend_analysis == "upward" and settings.get('trend_status') == "downward":
                        print(f"Buying {network}: Trending upward after a downward trend")
                        # Add code to buy the coin
                        settings['current_cost_usd'] = current_price * balance
                        settings['trend_status'] = "upward"

                    # Update trend status
                    if trend_analysis == "upward":
                        settings['trend_status'] = "upward"
                    elif trend_analysis == "downward":
                        settings['trend_status'] = "downward"

                    settings['current_price'] = current_price
                    settings['usd_value'] = balance * current_price
        update_coins_settings(coins_settings)
        time.sleep(refresh_interval)
