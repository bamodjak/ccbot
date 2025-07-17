import random
from utils.luhn import luhnify
from validation_api import fetch_bin_metadata

def generate_cards(bin_pattern: str, quantity: int, gateway: str = "auto"):
    cards = []
    metadata = fetch_bin_metadata(bin_pattern[:6])

    for _ in range(quantity):
        base = ''.join([str(random.randint(0, 9)) if c == 'x' else c for c in bin_pattern])
        cc = luhnify(base)
        mm = f"{random.randint(1, 12):02}"
        yy = f"{random.randint(25, 29)}"
        cvv = f"{random.randint(100, 999)}"
        card = f"{cc}|{mm}|{yy}|{cvv}"
        cards.append(card)

    if metadata:
        cards.insert(0, f"# BIN Metadata: {metadata.get('scheme', '')} {metadata.get('type', '')} {metadata.get('brand', '')}, Bank: {metadata.get('bank', '')}, Country: {metadata.get('country', '')}")

    return cards
