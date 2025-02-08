import re
import string
import json
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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


def to_shortcode(longid):
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
    base36_encoded = to_base(int(longid), 36)

    # Map each character to Instagram's alphabet
    return ''.join(to_ig_map[c] if c in to_ig_map else c for c in base36_encoded)


def load_extracted_parameters(file_path="extracted_params.json") -> dict:
    """Loads extracted parameters from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as infile:
            parameters = json.load(infile)
        return parameters
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading extracted parameters: {e}")
        return {}

def get_latest_post_media_id(session: requests.Session, page_name: str) -> str:
    """
    Fetches the latest post media ID for a given Instagram page.
    """
    
    extracted_params = load_extracted_parameters()

    if not extracted_params:
        logging.error("❌ Extracted parameters are missing or invalid.")
        return None
    print(extracted_params.get("jazoest", "2"))
    payload = {
        "av": extracted_params.get("av", "17841472251591209"),
        "__d": "www",
        "__user": extracted_params.get("__user", "0"),
        "__a": "1",
        "__req": extracted_params.get("__req", "7"),
        "__hs": extracted_params.get("__hs", "20123.HYP:instagram_web_pkg.2.1...1"),
        "dpr": extracted_params.get("dpr", "1"),
        "__ccg": extracted_params.get("__ccg", "MODERATE"),
        "__rev": extracted_params.get("__rev", "1019814589"),
        "__s": extracted_params.get("__s", "ogbayt:tcez1o:es29r3"),
        "__hsi": extracted_params.get("__hsi", "7467142648817593542"),
        "__comet_req": extracted_params.get("__comet_req", "7"),
        "fb_dtsg": extracted_params.get("fb_dtsg", "NAcMw7_GPycNRsJBCXi-B0BVEjmR39pFQ_tOBb7Zsa1nHc2axd4YsGQ:17864721031021537:1738415853"),
        "jazoest": extracted_params.get("jazoest", "26113"),
        "lsd": extracted_params.get("lsd", "o2qh5hkPEiMagabLkmLGw2"),
        "__spin_r": extracted_params.get("__spin_r", "1019812100"),
        "__spin_b": extracted_params.get("__spin_b", "trunk"),
        "__spin_t": extracted_params.get("__spin_t", "1738659746"),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "PolarisProfilePostsQuery",
        "variables": json.dumps({
            "data": {
                "count": 12,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True
            },
            "username": page_name, 
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True
        }),
        "server_timestamps": "true",
        "doc_id": extracted_params.get("doc_id", "8934560356598281")
    }
    response = session.post(url="https://www.instagram.com/graphql/query", data=payload)

    if response.status_code == 200:
        response_text = response.text  # Get raw text

        # Regular expression to find the first occurrence of "pk":"some_number"
        match = re.search(r'"pk":"(\d+)"', response_text)

        if match:
            print(match.group(1))
            return match.group(1)  # Extract and return the first PK found
        else:
            return None  # Return None if no PK is found
    else:
        logging.error(f"❌ Request failed with status code: {response.status_code}")
        return None  # Return None if request fails