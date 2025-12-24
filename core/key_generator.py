import secrets, string

def generate_key(tariff: str) -> str:
    tariff_map = {"baseus": "BASE", "standard": "STD", "premium": "PRE"}
    prefix = f"SHADOW-{tariff_map.get(tariff, 'CUS')}"
    seg1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    seg2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"{prefix}-{seg1}-{seg2}"
