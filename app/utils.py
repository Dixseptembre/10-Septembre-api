def clean_value(value):
    """
    NaN -> 0
    float others
    """
    return float(value) if value==value else 0