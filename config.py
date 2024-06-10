import yaml
import os

settings_folder = 'settings'
settings_file = os.path.join(settings_folder, 'settings.yaml')
coins_settings_file = os.path.join(settings_folder, 'coins_settings.yaml')

default_settings = {
    'key_name': "",
    'key_secret': '',
    'request_host': "api.coinbase.com",
    'accounts_path': "/api/v3/brokerage/accounts",
    'prices_path': "/api/v3/brokerage/products/{product_id}/ticker",
    'orders_path': "/api/v3/brokerage/orders",
    'spend_account': "USD",
    'refresh_interval': 60,
    'transaction_fee': 0.5,
    'sale_threshold': 10,
    'loss_limit': 5
}

default_settings_comments = """# Coinbase Developer Platform API - https://www.coinbase.com/settings/api
key_name: ""

# key_secret: The private key for the API, ensure newlines are escaped with \\n.
key_secret: ''

# request_host: The host for the Coinbase API.
request_host: "api.coinbase.com"

# accounts_path: The endpoint path for fetching account information.
accounts_path: "/api/v3/brokerage/accounts"

# prices_path: The endpoint path for fetching current prices. {product_id} will be replaced with the actual product ID.
prices_path: "/api/v3/brokerage/products/{product_id}/ticker"

# orders_path: The endpoint path for creating orders.
orders_path: "/api/v3/brokerage/orders"

# spend_account: The account used for spending, default is USD.
spend_account: "USD"

# Interval in seconds to refresh prices
refresh_interval: 60

# Transaction fee percentage
transaction_fee: 0.5

# Sale threshold percentage
sale_threshold: 10

# Loss limit percentage to trigger a sell
loss_limit: 5
"""

def ensure_settings_directory():
    if not os.path.exists(settings_folder):
        os.makedirs(settings_folder)
        print(f"Created directory {settings_folder}")

def ensure_settings_file():
    ensure_settings_directory()
    if not os.path.exists(settings_file):
        key_name = input("Enter your key name: ")
        key_secret = input("Enter your key secret: ")
        default_settings['key_name'] = key_name
        default_settings['key_secret'] = key_secret.replace("\n", "\\n")
        with open(settings_file, 'w') as file:
            file.write(default_settings_comments)
            yaml.dump(default_settings, file, default_flow_style=False)
        print(f"Created default {settings_file}")

def ensure_coins_settings_file():
    ensure_settings_directory()
    if not os.path.exists(coins_settings_file):
        with open(coins_settings_file, 'w') as file:
            yaml.dump({}, file)
        print(f"Created default {coins_settings_file}")

def load_settings():
    with open(settings_file, 'r') as file:
        return yaml.safe_load(file)

def load_coins_settings():
    with open(coins_settings_file, 'r') as file:
        return yaml.safe_load(file) or {}

def update_coins_settings(coins_settings):
    with open(coins_settings_file, 'w') as file:
        yaml.dump(coins_settings, file)

# Ensure files exist on import
ensure_settings_file()
ensure_coins_settings_file()
