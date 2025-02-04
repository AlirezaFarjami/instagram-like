import re


def extract_shortcode(instagram_url) -> str:
    """
    Extracts and returns the shortcode from an Instagram post or reel URL.
    
    Works for:
    - Posts: "https://www.instagram.com/p/DFiLS_II0aa/"
    - Reels: "https://www.instagram.com/username/reel/DFiIwE6u9ga/"
    
    Returns:
    - The shortcode (e.g., "DFiLS_II0aa" or "DFiIwE6u9ga") if found.
    - None if the URL does not match the expected format.
    """
    match = re.search(r'/(?:p|reel)/([^/]+)/', instagram_url)
    return match.group(1) if match else None

def from_shortcode(shortcode) -> str :
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

    intermediate = re.sub(r'\S', repl, shortcode)
    tokens = re.findall(r'<(\d+)>|(\w)', intermediate)

    total = 0
    for token in tokens:
        value = int(token[0]) if token[0] != '' else bigint_alphabet.index(token[1])
        total = total * 64 + value

    return str(total)