import random
import string

def random_digits(length: int):
    return ''.join(random.choices(string.digits, k=length))

def random_letters(length: int):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

def random_token(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
