import random
import requests
import os
from utils.luhn import luhnify

def fetch_bin_metadata(bin_number):
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", headers={"Accept-Version": "3"})
        if response.status_code == 200:
            data = response.json()
            return {
                "scheme": data.get("scheme"),
                "type": data.get("type"),
                "brand": data.get("brand"),
                "bank": data.get("bank", {}).get("name"),
                "country": data.get("country", {}).get("name")
            }
    except Exception:
        pass
    return {}

def detect_gateway(token: str) -> str:
    if token.startswith("sk_test") or token.startswith("sk_live"):
        return "stripe"
    elif token.startswith("access_token$production") or token.startswith("access_token$sandbox"):
        return "paypal"
    elif token.startswith("AQ"):
        return "adyen"
    else:
        return "unknown"

def validate_card_gateway(card_str: str, token: str, gateway: str):
    if gateway == "stripe":
        try:
            import stripe
            stripe.api_key = token
            cc, mm, yy, cvv = card_str.strip().split('|')
            token_obj = stripe.Token.create(card={
                'number': cc,
                'exp_month': int(mm),
                'exp_year': int('20' + yy) if len(yy) == 2 else int(yy),
                'cvc': cvv
            })
            pm = stripe.PaymentMethod.create(type='card', card={'token': token_obj.id})
            if pm and pm.card and pm.card.checks.get('cvc_check') == 'pass':
                return '✅ Approved'
            return '❌ Declined'
        except Exception:
            return '⚠️ Stripe Error'

    elif gateway == "paypal":
        return '✅ Simulated PayPal Approval'

    elif gateway == "adyen":
        return '✅ Simulated Adyen Approval'

    else:
        return '❌ Unknown gateway'
