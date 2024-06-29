import os
import yaml
from pathlib import Path


def ensure_settings_file():
    settings_dir = Path("settings")
    settings_file = settings_dir / "settings.yaml"
    coins_settings_file = settings_dir / "coins_settings.yaml"
    trends_dir = Path("data/trends")

    settings_dir.mkdir(parents=True, exist_ok=True)
    trends_dir.mkdir(parents=True, exist_ok=True)

    if not settings_file.exists():
        default_settings = {
            "key_name": "organizations/{org_id}/apiKeys/{key_id}",  # Your API key name
            "key_secret": "",  # Your API key secret
            "request_host": "api.coinbase.com",  # The host for the Coinbase API
            "accounts_path": "/api/v3/brokerage/accounts",  # The endpoint path for fetching account information
            "prices_path": "/api/v3/brokerage/products/{product_id}/ticker",
            # The endpoint path for fetching current prices
            "orders_path": "/api/v3/brokerage/orders",  # The endpoint path for creating orders
            "spend_account": "USD",  # The account used for spending
            "refresh_interval": 60,  # Interval in seconds to refresh prices
            "transaction_fee": 0.5,  # Transaction fee percentage
            "sale_threshold": 10,  # Sale threshold percentage
            "loss_limit": 5  # Loss limit percentage to trigger a sell
        }

        comments = {
            "key_name": "Coinbase Developer Platform API key name",
            "key_secret": "The private key for the API, ensure newlines are escaped with \\n",
            "request_host": "The host for the Coinbase API",
            "accounts_path": "The endpoint path for fetching account information",
            "prices_path": "The endpoint path for fetching current prices. {product_id} will be replaced with the actual product ID",
            "orders_path": "The endpoint path for creating orders",
            "spend_account": "The account used for spending, default is USD",
            "refresh_interval": "Interval in seconds to refresh prices",
            "transaction_fee": "Transaction fee percentage",
            "sale_threshold": "Sale threshold percentage",
            "loss_limit": "Loss limit percentage to trigger a sell"
        }

        with open(settings_file, "w") as f:
            yaml.dump(default_settings, f, default_flow_style=False, sort_keys=False)
        print(f"Created default settings file at {settings_file}")

        # Add comments to the settings file
        with open(settings_file, "r") as f:
            lines = f.readlines()

        with open(settings_file, "w") as f:
            for line in lines:
                key = line.split(":")[0].strip()
                if key in comments:
                    f.write(f"# {comments[key]}\n")
                f.write(line)

    if not coins_settings_file.exists():
        default_coins_settings = {}
        with open(coins_settings_file, "w") as f:
            yaml.dump(default_coins_settings, f)
        print(f"Created default coins settings file at {coins_settings_file}")


def load_settings():
    ensure_settings_file()
    settings_file = Path("settings/settings.yaml")
    with open(settings_file, "r") as f:
        settings = yaml.safe_load(f)

    if not settings['key_name'] or not settings['key_secret']:
        settings['key_name'] = input("Enter your Coinbase API key name: ")
        settings['key_secret'] = input("Enter your Coinbase API key secret: ").replace("\\n", "\n")
        with open(settings_file, "w") as f:
            yaml.dump(settings, f, default_flow_style=False, sort_keys=False)

    return settings


def load_coins_settings():
    ensure_settings_file()
    with open("settings/coins_settings.yaml", "r") as f:
        return yaml.safe_load(f)


def save_trends(network, trends):
    trends_file = Path(f"data/trends/{network}.yaml")
    with open(trends_file, "w") as f:
        yaml.dump(trends, f)


def load_trends(network):
    trends_file = Path(f"data/trends/{network}.yaml")
    if trends_file.exists():
        with open(trends_file, "r") as f:
            return yaml.safe_load(f)
    return []


def update_coins_settings(settings):
    with open("settings/coins_settings.yaml", "w") as f:
        yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
