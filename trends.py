from coinbase import get_current_price
from config import load_coins_settings, update_coins_settings
import numpy as np

coins_settings = load_coins_settings()

def calculate_sma(prices, window):
    if len(prices) < window:
        return None  # Not enough data to calculate SMA
    return np.mean(prices[-window:])
    
def check_price_trends():
    short_term_window = 10
    long_term_window = 30 
    
    for coin, details in coins_settings.items():
        if details.get('enabled', False):
            previous_price = details.get('previous_price')
            current_price = get_current_price(f"{coin}-USD")
            balance = details.get('balance', 0)
            current_cost_usd = details.get('current_cost_usd', -1)

            if current_price is not None:
                details['prices'].append(current_price)
                if previous_price is not None:
                    price_change = (current_price - previous_price) / previous_price
                else:
                    price_change = 0

                details['price_trends'].append(price_change)
                if len(details['price_trends']) > short_term_window:
                    details['price_trends'].pop(0)

                details['previous_price'] = current_price
                details['current_price'] = current_price
                details['usd_value'] = current_price * balance

                # Calculate SMA
                details['sma_short_term'] = calculate_sma(details['prices'], short_term_window)
                details['sma_long_term'] = calculate_sma(details['prices'], long_term_window)

                # Determine trend status using SMA
                if details['sma_short_term'] and details['sma_long_term']:
                    if details['sma_short_term'] > details['sma_long_term']:
                        trend_status = 'upward'
                    elif details['sma_short_term'] < details['sma_long_term']:
                        trend_status = 'downward'
                    else:
                        trend_status = 'stable'
                else:
                    trend_status = 'stable'

                details['trend_status'] = trend_status
                
                update_coins_settings(coins_settings)
            else:
                print(f"Could not retrieve current price for {coin}. Skipping...")
