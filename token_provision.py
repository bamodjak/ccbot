import random
import string

def generate_stripe_token(mode="test"):
    prefix = "sk_test_" if mode == "test" else "sk_live_"
    body = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    return prefix + body

def generate_paypal_token(mode="test"):
    prefix = "access_token$sandbox$" if mode == "test" else "access_token$production$"
    body = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
    return prefix + body

def generate_adyen_token(mode="test"):
    prefix = "AQEV" if mode == "test" else "AQEL"
    body = ''.join(random.choices(string.ascii_letters + string.digits, k=56))
    return prefix + body

def generate_dummy_token(gateway, mode):
    return f"{gateway}_{mode}_" + ''.join(random.choices(string.ascii_letters + string.digits, k=36))

def generate_token(gateway: str, mode: str = "test"):
    if gateway == "stripe":
        return generate_stripe_token(mode)
    elif gateway == "paypal":
        return generate_paypal_token(mode)
    elif gateway == "adyen":
        return generate_adyen_token(mode)
    else:
        return generate_dummy_token(gateway, mode)
