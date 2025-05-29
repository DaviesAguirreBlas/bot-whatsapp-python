def normalize_amount(amount_str: str) -> float:
    """Normalize amount string to float (remove currency symbols, commas, etc)."""
    return float(amount_str.replace('S/', '').replace(',', '').strip()) 