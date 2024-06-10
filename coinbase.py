import jwt
import time
import secrets
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import load_settings

settings = load_settings()
if settings is None:
    raise ValueError("Failed to load settings")

key_name = settings['key_name']
key_secret = settings['key_secret'].replace('\\n', '\n')  # Ensure newlines are correctly interpreted
request_host = settings['request_host']
accounts_path = settings['accounts_path']
prices_path = settings['prices_path']
orders_path = settings['orders_path']


def build_jwt(uri):
    private_key_bytes = key_secret.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None, backend=default_backend())
    jwt_payload = {
        'sub': key_name,
        'iss': "cdp",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'uri': uri,
    }
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_name, 'nonce': secrets.token_hex()},
    )
    return jwt_token


def make_request(path):
    uri = f"GET {request_host}{path}"
    jwt_token = build_jwt(uri)
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.get(f"https://{request_host}{path}", headers=headers)
    response.raise_for_status()
    return response.json()


def get_accounts():
    return make_request(accounts_path)['accounts']


def get_current_price(product_id):
    try:
        response = make_request(prices_path.format(product_id=product_id))
        return float(response.get('price', 0))  # Return 0 if 'price' is not found
    except requests.HTTPError as e:
        print(f"HTTP error for {product_id}: {e}")
        return None


def place_market_order(product_id, side, size=None, usd_order_size=None):
    if not size and not usd_order_size:
        raise ValueError("Either size or usd_order_size must be provided")

    payload = {
        "client_order_id": secrets.token_hex(),
        "product_id": product_id,
        "side": side,
        "order_configuration": {
            "market_market_ioc": {
                "quote_size": str(usd_order_size) if usd_order_size else None,
                "base_size": str(size) if size else None
            }
        }
    }
    try:
        response = requests.post(f"https://{request_host}{orders_path}", json=payload)
        response.raise_for_status()
        return True, response.json()['order_id'], None
    except requests.HTTPError as e:
        return False, None, str(e)


def place_limit_order(product_id, side, base_size, limit_price):
    payload = {
        "client_order_id": secrets.token_hex(),
        "product_id": product_id,
        "side": side,
        "order_configuration": {
            "limit_limit_gtc": {
                "base_size": str(base_size),
                "limit_price": str(limit_price)
            }
        }
    }
    try:
        response = requests.post(f"https://{request_host}{orders_path}", json=payload)
        response.raise_for_status()
        return True, response.json()['order_id'], None
    except requests.HTTPError as e:
        return False, None, str(e)


def cancel_order(order_id):
    path = f"/api/v3/brokerage/orders/historical/{order_id}/cancel"
    try:
        response = requests.post(f"https://{request_host}{path}")
        response.raise_for_status()
        return True, None
    except requests.HTTPError as e:
        return False, str(e)
