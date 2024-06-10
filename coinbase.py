import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets
import requests
import json
from config import load_settings

config = load_settings()

key_name = config['key_name']
key_secret = config['key_secret'].replace("\\n", "\n")
request_host = config['request_host']

def build_jwt(uri):
    try:
        private_key_bytes = key_secret.encode('utf-8')
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    except Exception as e:
        print(f"Error loading private key: {e}")
        raise

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

def make_request(path, method="GET", payload=None):
    uri = f"{method} {request_host}{path}"
    jwt_token = build_jwt(uri)
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    url = f'https://{request_host}{path}'
    if method == "POST":
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    else:
        response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def get_accounts():
    accounts_path = config['accounts_path']
    return make_request(accounts_path).get('accounts', [])

def get_current_price(product_id):
    prices_path = config['prices_path'].format(product_id=product_id)
    try:
        price_response = make_request(prices_path)
        # Extract the latest price from the response
        try:
            return float(price_response['best_bid'])
        except KeyError:
            return float(price_response['trades'][0]['price'])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"HTTP error for {product_id}: {e}")
            return None
        else:
            print(f"HTTP error for {product_id}: {e}")
    except Exception as e:
        print(f"Error retrieving price for {product_id}: {e}")
    return None

def place_order(product_id, side, size):
    orders_path = config['orders_path']
    order_payload = {
        "product_id": product_id,
        "side": side,
        "order_configuration": {
            "market_market_ioc": {
                "base_size": size
            }
        }
    }
    try:
        order_response = make_request(orders_path, method="POST", payload=order_payload)
        return order_response.get('success', False), order_response.get('order_id', None), order_response.get('error_response', {})
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error placing order for {product_id}: {e}")
        return False, None, str(e)
    except Exception as e:
        print(f"Error placing order for {product_id}: {e}")
        return False, None, str(e)
