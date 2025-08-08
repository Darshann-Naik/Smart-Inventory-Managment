# /core/utils.py

def generate_acronym(text: str, num_chars: int = 3) -> str:
    """
    Generates a simple acronym from a string by taking the first letter
    of the first few words.

    Args:
        text: The input string (e.g., "Parle-G Biscuit").
        num_chars: The desired number of characters in the acronym.

    Returns:
        An uppercase acronym (e.g., "PGB").
    """
    if not text:
        return ""
    
    words = text.split()
    acronym = "".join(word[0] for word in words[:num_chars])
    
    return acronym.upper()