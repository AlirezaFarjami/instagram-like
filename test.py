import re

def extract_shortcode(instagram_url):
    """
    Extracts and returns the shortcode from an Instagram post URL.
    
    For example, given:
      "https://www.instagram.com/p/DFiLS_II0aa/"
    it returns:
      "DFiLS_II0aa"
    
    If the URL does not match the expected format, the function returns None.
    """
    match = re.search(r'/p/([^/]+)/', instagram_url)
    if match:
        return match.group(1)
    return None

def from_shortcode(shortcode):
    """
    Converts an Instagram-style shortcode back into its media id (as a decimal string).

    The function relies on two custom alphabets:
      - ig_alphabet: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
      - bigint_alphabet: "0123456789abcdefghijklmnopqrstuvwxyz"

    The original conversion worked as follows:
      - A number was first represented in base 64 using digits from bigint_alphabet for values 0-35,
        and a token of the form <n> for values 36-63.
      - Then each digit was replaced with a corresponding character from ig_alphabet.

    This function reverses that process.
    """
    # Define alphabets.
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = lower.upper()
    numbers = '0123456789'
    ig_alphabet = upper + lower + numbers + '-_'
    bigint_alphabet = numbers + lower  # "0123456789abcdefghijklmnopqrstuvwxyz"

    # First, map each character of the shortcode back into the "bigint_alphabet" representation.
    # For each non-space character:
    #   - Find its index in ig_alphabet.
    #   - If that index is within the length of bigint_alphabet (i.e. 36), then its digit is the
    #     character at that position in bigint_alphabet.
    #   - Otherwise, represent it as a token of the form <index>.
    def repl(match):
        ch = match.group(0)
        idx = ig_alphabet.index(ch)
        # For digits 0-35, return the corresponding character;
        # for values 36-63, we need to preserve the full numeric value in a token.
        return bigint_alphabet[idx] if idx < len(bigint_alphabet) else f"<{idx}>"

    # Reconstruct the intermediate string, which is in the "bigint_alphabet" format (with possible <n> tokens).
    intermediate = re.sub(r'\S', repl, shortcode)

    # Now, tokenize the intermediate string.
    # The tokens are either:
    #   - A token of the form <number> (for digits 36-63), or
    #   - A single alphanumeric character (for digits 0-35).
    tokens = re.findall(r'<(\d+)>|(\w)', intermediate)

    # Interpret the tokens as digits of a base-64 number.
    total = 0
    for token in tokens:
        if token[0] != '':  # This token is from a <n> pattern.
            value = int(token[0])
        else:
            # Otherwise, token[1] is a single digit character from bigint_alphabet.
            value = bigint_alphabet.index(token[1])
        total = total * 64 + value

    return str(total)


# Example usage:
if __name__ == '__main__':
    url = "https://www.instagram.com/p/DE8JNKqgfhq/"
    shortcode = extract_shortcode(url)
    print("Extracted shortcode:", shortcode)
    media_id = from_shortcode(shortcode)
    print("Media ID:", media_id)