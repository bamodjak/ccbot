from validation_api import detect_gateway, validate_card_gateway

def batch_validate(card_list, token, forced_gateway=None):
    gateway = forced_gateway or detect_gateway(token)
    return [(card, validate_card_gateway(card, token, gateway)) for card in card_list]
