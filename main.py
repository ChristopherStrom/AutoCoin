import time
import json
from datetime import datetime, timedelta
import coinbase.wallet.client as client
from collections import deque

# Load settings from settings.json
with open('settings.json', 'r') as f:
    settings = json.load(f)

API_KEY = settings['API_KEY']
API_SECRET = settings['API_SECRET']
daily_spend_limit = settings['daily_spend_limit']
daily_earned_limit = settings['daily_earned_limit']
transaction_rate_limit = settings['transaction_rate_limit']

# Initialize the Coinbase client
coinbase_client = client.Client(API_KEY, API_SECRET)

# Define your coins and thresholds
coins = {
    'BTC': {'purchase_price': None, 'history': deque(maxlen=43200), 'balance': 0},
    'SHIB': {'purchase_price': None, 'history': deque(maxlen=43200), 'balance': 0},
    'DOGE': {'purchase_price': None, 'history': deque(maxlen=43200), 'balance': 0},
}

daily_spent = 0
daily_earned = 0
last_transaction_time = datetime.now() - timedelta(seconds=transaction_rate_limit)

start_of_day = datetime.now().date()


def reset_daily_limits():
    global daily_spent, daily_earned, start_of_day
    if datetime.now().date() > start_of_day:
        daily_spent = 0
        daily_earned = 0
        start_of_day = datetime.now().date()


def get_current_price(currency_pair):
    try:
        price = coinbase_client.get_spot_price(currency_pair=f'{currency_pair}-USD')
        return float(price['amount'])
    except Exception as e:
        print(f"Error fetching price for {currency_pair}: {e}")
        return None


def place_buy_order(currency_pair, amount, price):
    global daily_spent, coins, last_transaction_time
    if (datetime.now() - last_transaction_time).seconds < transaction_rate_limit:
        print(f"Transaction rate limit reached. Skipping buy for {currency_pair}")
        return None
    try:
        account = coinbase_client.get_primary_account()
        buy_order = account.buy(amount=amount, currency=currency_pair)
        print(f"Buy order placed for {currency_pair}: {buy_order}")
        daily_spent += price * float(amount)
        coins[currency_pair]['balance'] += float(amount)
        coins[currency_pair]['purchase_price'] = ((coins[currency_pair]['purchase_price'] or 0) * (
                    coins[currency_pair]['balance'] - float(amount)) + price * float(amount)) / coins[currency_pair][
                                                     'balance']
        last_transaction_time = datetime.now()
        return buy_order
    except Exception as e:
        print(f"Error placing buy order for {currency_pair}: {e}")
        return None


def place_sell_order(currency_pair, amount, price):
    global daily_earned, coins, last_transaction_time
    if (datetime.now() - last_transaction_time).seconds < transaction_rate_limit:
        print(f"Transaction rate limit reached. Skipping sell for {currency_pair}")
        return None
    try:
        account = coinbase_client.get_primary_account()
        sell_order = account.sell(amount=amount, currency=currency_pair)
        print(f"Sell order placed for {currency_pair}: {sell_order}")
        daily_earned += price * float(amount)
        coins[currency_pair]['balance'] -= float(amount)
        if coins[currency_pair]['balance'] == 0:
            coins[currency_pair]['purchase_price'] = None
        last_transaction_time = datetime.now()
        return sell_order
    except Exception as e:
        print(f"Error placing sell order for {currency_pair}: {e}")
        return None


def analyze_trend(history):
    if len(history) < 2:
        return None
    return 'up' if history[-1] > history[0] else 'down'


def buy_coin(coin, current_price):
    global coins
    if daily_spent + current_price <= daily_spend_limit:
        print(f"Buying {coin} at ${current_price}")
        buy_order = place_buy_order(coin, '1.0', current_price)  # Assuming you want to buy 1 unit
        if buy_order:
            coins[coin]['purchase_price'] = current_price
    else:
        print(f"Daily spend limit reached. Cannot buy {coin} at ${current_price}")


def sell_coin(coin, current_price):
    global coins
    if daily_earned + current_price <= daily_earned_limit:
        print(f"Selling {coin} at ${current_price}")
        sell_order = place_sell_order(coin, '1.0', current_price)  # Assuming you want to sell 1 unit
        if sell_order:
            coins[coin]['purchase_price'] = None
    else:
        print(f"Daily earned limit reached. Cannot sell {coin} at ${current_price}")


def get_initial_holdings():
    accounts = coinbase_client.get_accounts()
    for account in accounts.data:
        currency = account['balance']['currency']
        if currency in coins:
            balance = float(account['balance']['amount'])
            if balance > 0:
                transactions = coinbase_client.get_account_transactions(account['id'])
                total_cost = 0
                total_amount = 0
                for transaction in transactions.data:
                    if transaction['type'] == 'buy':
                        total_cost += float(transaction['native_amount']['amount'])
                        total_amount += float(transaction['amount']['amount'])
                average_cost = total_cost / total_amount if total_amount > 0 else None
                coins[currency]['balance'] = balance
                coins[currency]['purchase_price'] = average_cost
                print(f"Initialized {currency}: Balance = {balance}, Average Cost = {average_cost}")


def check_thresholds():
    reset_daily_limits()
    for coin, data in coins.items():
        current_price = get_current_price(coin)
        if current_price:
            data['history'].append(current_price)
            trend = analyze_trend(data['history'])
            print(f"{datetime.now()}: Current price of {coin}: ${current_price}, Trend: {trend}")

            if trend == 'down' and (data['purchase_price'] is None or current_price < data['purchase_price']):
                buy_coin(coin, current_price)
            elif trend == 'up' and data['purchase_price'] and current_price > data['purchase_price'] * 1.05:
                sell_coin(coin, current_price)


# Get initial holdings on startup
get_initial_holdings()

while True:
    check_thresholds()
    time.sleep(60)  # Wait for 1 minute before checking again
