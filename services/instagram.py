import requests
import logging
import json
import re
from database.repositories import load_extracted_parameters

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_latest_post_media_id(session: requests.Session, account_username: str, page_username: str) -> str:
    """
    Fetches the latest post media ID for a given Instagram target_username, using the parameters
    extracted from extract_username.
    
    Parameters:
    - session: The requests.Session object with necessary cookies.
    - extract_username: The username used to extract parameters for the request.
    - target_username: The username of the Instagram account for which we want to fetch the latest post media ID.
    
    Returns:
    - The media ID of the latest post if successful, None otherwise.
    """
    
    # Load extracted parameters for the given extract_username
    extracted_params = load_extracted_parameters(account_username )

    if not extracted_params:
        logging.error("❌ Extracted parameters are missing or invalid.")
        return None

    # Logging for debugging purposes
    logging.info(f"Extracted parameters for {account_username }: {extracted_params}")

    # Construct the payload using the extracted parameters
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
            "username": page_username,  # Use the target username to fetch latest post
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True
        }),
        "server_timestamps": "true",
        "doc_id": extracted_params.get("doc_id", "8934560356598281")
    }

    # Send POST request to Instagram's GraphQL API
    response = session.post(url="https://www.instagram.com/graphql/query", data=payload)

    if response.status_code == 200:
        response_text = response.text  # Get raw text

        # Regular expression to find the first occurrence of "pk":"some_number"
        match = re.search(r'"pk":"(\d+)"', response_text)

        if match:
            media_id = match.group(1)
            logging.info(f"✅ Latest post media ID for {page_username}: {media_id}")
            return media_id  # Return the media ID
        else:
            logging.error("❌ No media ID (pk) found in the response.")
            return None
    else:
        logging.error(f"❌ Request failed with status code: {response.status_code}")
        return None  # Return None if request fails
