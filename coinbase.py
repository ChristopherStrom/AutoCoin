import requests
import jwt
import time
import secrets
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import load_settings
import json
import math

settings = load_settings()
key_name = settings['key_name']
key_secret = settings['key_secret'].replace("\\n", "\n")
request_host = settings['request_host']


def generate_jwt(uri):
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


def make_request(path, method="GET", payload=None):
    uri = f"{method} {request_host}{path}"
    jwt_token = generate_jwt(uri)
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    url = f'https://{request_host}{path}'
    if method == "POST":
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    else:
        response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"HTTP error for {url}: {response.status_code} {response.reason}")
        print(response.text)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def get_accounts():
    accounts_path = settings['accounts_path']
    return make_request(accounts_path).get('accounts', [])


def get_current_price(product_id):
    prices_path = settings['prices_path'].format(product_id=product_id)
    try:
        price_response = make_request(prices_path)
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


def get_product_info(product_id):
    products_path = "/api/v3/brokerage/products"
    try:
        response = make_request(products_path)
        products = response.get('products', [])
        for product in products:
            if product['product_id'] == product_id:
                return product
    except Exception as e:
        print(f"Error retrieving product information for {product_id}: {e}")
    return None


def place_market_order(product_id, side, usd_order_size=None, size=None):
    orders_path = settings['orders_path']
    product_info = get_product_info(product_id)

    if product_info is None:
        print("Error: Unable to fetch product information.")
        return False, None, "Unable to fetch product information"

    base_currency_price_increment = abs(round(math.log10(float(product_info['base_increment']))))

    current_price = get_current_price(product_id)

    if current_price is None:
        print(f"Error: Unable to fetch current price for {product_id}")
        return False, None, "Unable to fetch current price"

    if usd_order_size:
        order_size = usd_order_size / current_price
    else:
        order_size = size

    if size and order_size > size:
        order_size = size

    order_size = math.floor(order_size * (10 ** base_currency_price_increment)) / (10 ** base_currency_price_increment)
    formatted_size = f"{order_size:.{base_currency_price_increment}f}"

    order_payload = {
        "client_order_id": secrets.token_hex(16),
        "product_id": product_id,
        "side": side,
        "order_configuration": {
            "market_market_ioc": {
                "base_size": formatted_size
            }
        }
    }

    try:
        print(f"Placing order with payload: {order_payload}")
        order_response = make_request(orders_path, method="POST", payload=order_payload)
        return order_response.get('success', False), order_response.get('order_id', None), order_response.get(
            'error_response', {})
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error placing order for {product_id}: {e}")
        return False, None, str(e)
    except Exception as e:
        print(f"Error placing order for {product_id}: {e}")
        return False, None, str(e)


def place_limit_order(product_id, side, base_size, limit_price):
    orders_path = settings['orders_path']
    product_info = get_product_info(product_id)

    if product_info is None:
        print("Error: Unable to fetch product information.")
        return False, None, "Unable to fetch product information"

    base_currency_price_increment = abs(round(math.log10(float(product_info['base_increment']))))
    quote_currency_price_increment = abs(round(math.log10(float(product_info['quote_increment']))))

    formatted_size = f"{base_size:.{base_currency_price_increment}f}"
    formatted_price = f"{limit_price:.{quote_currency_price_increment}f}"

    order_payload = {
        "client_order_id": secrets.token_hex(16),
        "product_id": product_id,
        "side": side,
        "order_configuration": {
            "limit_limit_gtc": {
                "base_size": formatted_size,
                "limit_price": formatted_price
            }
        }
    }

    try:
        print(f"Placing order with payload: {order_payload}")
        order_response = make_request(orders_path, method="POST", payload=order_payload)
        return order_response.get('success', False), order_response.get('order_id', None), order_response.get(
            'error_response', {})
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error placing order for {product_id}: {e}")
        return False, None, str(e)
    except Exception as e:
        print(f"Error placing order for {product_id}: {e}")
        return False, None, str(e)


def cancel_order(order_id):
    cancel_path = "/api/v3/brokerage/orders/batch_cancel"
    payload = {
        "order_ids": [order_id]
    }

    try:
        response = make_request(cancel_path, method="POST", payload=payload)
        return response.get('results', [])[0].get('success', False)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error canceling order {order_id}: {e}")
        return False
    except Exception as e:
        print(f"Error canceling order {order_id}: {e}")
        return False
