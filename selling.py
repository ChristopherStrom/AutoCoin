from coinbase import get_current_price, place_market_order, place_limit_order
from config import load_coins_settings, update_coins_settings

coins_settings = load_coins_settings()


def sell_coin(coin, balance):
    print(f"Selling {coin}: Testing sale with unknown cost.")
    if balance <= 0:
        print(f"No balance available to sell for {coin}.")
        return

    success, order_id, error = place_market_order(f"{coin}-USD", "SELL", size=balance)
    if success:
        print(f"Sell order placed successfully for {coin}, order ID: {order_id}")
        # Update balance and sell details
        current_price = get_current_price(f"{coin}-USD")
        sell_amount = balance * current_price
        profit = sell_amount - (balance * coins_settings[coin]['current_cost_usd'])
        coins_settings[coin]['balance'] = 0
        coins_settings[coin]['usd_value'] = 0
        coins_settings[coin]['last_sell_price'] = current_price
        coins_settings[coin]['last_sell_amount'] = sell_amount
        coins_settings[coin]['total_profit'] = coins_settings[coin].get('total_profit', 0) + profit
        coins_settings[coin]['total_gain_loss'] = (sell_amount - coins_settings[coin]['current_cost_usd'] * balance)
        update_coins_settings(coins_settings)
    else:
        print(f"Failed to place sell order for {coin}: {error}")


def check_sell_opportunities():
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

                # Check if we should place a sell order
                if current_cost_usd == -1:
                    sell_coin(coin, balance)
                else:
                    # Example of placing a limit order
                    limit_price = current_price * 1.05  # 5% above current price
                    success, order_id, error = place_limit_order(f"{coin}-USD", "SELL", base_size=balance,
                                                                 limit_price=limit_price)
                    if success:
                        print(f"Limit sell order placed successfully for {coin}, order ID: {order_id}")
                        # Update balance and sell details
                        sell_amount = balance * limit_price
                        profit = sell_amount - (balance * coins_settings[coin]['current_cost_usd'])
                        coins_settings[coin]['balance'] = 0
                        coins_settings[coin]['usd_value'] = 0
                        coins_settings[coin]['last_sell_price'] = limit_price
                        coins_settings[coin]['last_sell_amount'] = sell_amount
                        coins_settings[coin]['total_profit'] = coins_settings[coin].get('total_profit', 0) + profit
                        coins_settings[coin]['total_gain_loss'] = (
                                    sell_amount - coins_settings[coin]['current_cost_usd'] * balance)
                        update_coins_settings(coins_settings)
                    else:
                        print(f"Failed to place limit sell order for {coin}: {error}")

                update_coins_settings(coins_settings)
            else:
                print(f"Could not retrieve current price for {coin}. Skipping...")
