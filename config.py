import os
import ruamel.yaml

SETTINGS_PATH = "settings/settings.yaml"
COINS_SETTINGS_PATH = "settings/coins_settings.yaml"

default_settings = {
    'key_name': '',
    'key_secret': '',
    'request_host': 'api.coinbase.com',
    'accounts_path': '/api/v3/brokerage/accounts',
    'prices_path': '/api/v3/brokerage/products/{product_id}/ticker',
    'orders_path': '/api/v3/brokerage/orders',
    'spend_account': 'USD',
    'refresh_interval': 60,
    'transaction_fee': 0.5,
    'sale_threshold': 10,
    'loss_limit': 5
}

default_settings_comments = {
    'key_name': 'Coinbase Developer Platform API - https://www.coinbase.com/settings/api',
    'key_secret': 'The private key for the API, ensure newlines are escaped with \\n.',
    'request_host': 'The host for the Coinbase API.',
    'accounts_path': 'The endpoint path for fetching account information.',
    'prices_path': 'The endpoint path for fetching current prices. {product_id} will be replaced with the actual product ID.',
    'orders_path': 'The endpoint path for creating orders.',
    'spend_account': 'The account used for spending, default is USD.',
    'refresh_interval': 'Interval in seconds to refresh prices.',
    'transaction_fee': 'Transaction fee percentage.',
    'sale_threshold': 'Sale threshold percentage.',
    'loss_limit': 'Loss limit percentage to trigger a sell.'
}

default_coins_settings = {}

yaml = ruamel.yaml.YAML()

def ensure_settings_file():
    if not os.path.exists(SETTINGS_PATH):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        settings_data = ruamel.yaml.comments.CommentedMap(default_settings)
        for key, comment in default_settings_comments.items():
            settings_data.yaml_set_comment_before_after_key(key, before=comment)
        with open(SETTINGS_PATH, 'w') as f:
            yaml.dump(settings_data, f)
        print(f"Created default settings file at {SETTINGS_PATH}")
        # Prompt for API details
        key_name = input("Enter your key_name: ")
        key_secret = input("Enter your key_secret: ")
        settings_data['key_name'] = key_name
        settings_data['key_secret'] = key_secret
        with open(SETTINGS_PATH, 'w') as f:
            yaml.dump(settings_data, f)

def ensure_coins_settings_file():
    if not os.path.exists(COINS_SETTINGS_PATH):
        os.makedirs(os.path.dirname(COINS_SETTINGS_PATH), exist_ok=True)
        with open(COINS_SETTINGS_PATH, 'w') as f:
            yaml.dump(default_coins_settings, f)
        print(f"Created default coins settings file at {COINS_SETTINGS_PATH}")

def load_settings():
    ensure_settings_file()
    with open(SETTINGS_PATH, 'r') as f:
        return yaml.load(f)

def load_coins_settings():
    ensure_coins_settings_file()
    with open(COINS_SETTINGS_PATH, 'r') as f:
        return yaml.load(f)

def update_coins_settings(coins_settings):
    with open(COINS_SETTINGS_PATH, 'w') as f:
        yaml.dump(coins_settings, f)
