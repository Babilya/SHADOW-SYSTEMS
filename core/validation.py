import re

def validate_key(key: str) -> bool:
    return key.startswith("SHADOW-") and len(key) == 20

def validate_username(username: str) -> bool:
    return re.match(r'^@?[a-zA-Z0-9_]{5,32}$', username) is not None
