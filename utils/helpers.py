def format_price(price: int) -> str:
    return f"{price:,}".replace(",", " ") + " ₴"

def truncate_text(text: str, max_len: int = 100) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text
