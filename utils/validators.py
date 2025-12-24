import re

def is_valid_key(key: str) -> bool:
    return key.startswith("SHADOW-") and key.count("-") == 3

def is_valid_username(username: str) -> bool:
    return re.match(r'^[a-zA-Z0-9_]{3,32}$', username.lstrip("@")) is not None
