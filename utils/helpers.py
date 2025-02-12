import re
import string
import json
import logging
import requests

from database.repositories import load_extracted_parameters

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_shortcode(post_url) -> str:
    """
    Extracts and returns the shortcode from an Instagram post or reel URL.
    
    Works for:
    - Posts: "https://www.instagram.com/p/DFiLS_II0aa/"
    - Reels: "https://www.instagram.com/username/reel/DFiIwE6u9ga/"
    
    Returns:
    - The shortcode (e.g., "DFiLS_II0aa" or "DFiIwE6u9ga") if found.
    - None if the URL does not match the expected format.
    """
    match = re.search(r'/(?:p|reel)/([^/]+)/', post_url)
    return match.group(1) if match else None

def from_shortcode(post_shortcode) -> str :
    """
    Converts an Instagram-style shortcode back into its media id (as a decimal string).
    """
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = lower.upper()
    numbers = '0123456789'
    ig_alphabet = upper + lower + numbers + '-_'
    bigint_alphabet = numbers + lower

    def repl(match):
        ch = match.group(0)
        idx = ig_alphabet.index(ch)
        return bigint_alphabet[idx] if idx < len(bigint_alphabet) else f"<{idx}>"

    intermediate = re.sub(r'\S', repl, post_shortcode)
    tokens = re.findall(r'<(\d+)>|(\w)', intermediate)

    total = 0
    for token in tokens:
        value = int(token[0]) if token[0] != '' else bigint_alphabet.index(token[1])
        total = total * 64 + value

    return str(total)

def to_shortcode(media_id) -> str:
    """
    Converts a decimal number (as string or int) into an Instagram-style shortcode.
    """
    # Define character sets
    numbers = '0123456789'
    lower = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    upper = string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    # Instagram-style base-64 alphabet
    ig_alphabet = upper + lower + numbers + '-_'  # Standard Instagram-like shortcode alphabet
    bigint_alphabet = numbers + lower  # The bigint encoding alphabet (base-36)
    
    # Mapping dictionary
    to_ig_map = {bigint_alphabet[i]: ig_alphabet[i] for i in range(len(bigint_alphabet))}
    
    # Base conversion (decimal → base 36)
    def to_base(n, base=36):
        """ Convert a decimal number to a given base (as a string). """
        if n == 0:
            return '0'
        digits = []
        while n:
            digits.append(bigint_alphabet[n % base])
            n //= base
        return ''.join(digits[::-1])
    
    # Convert longid to base-36 string
    base36_encoded = to_base(int(media_id), 36)

    # Map each character to Instagram's alphabet
    return ''.join(to_ig_map[c] if c in to_ig_map else c for c in base36_encoded)

