import requests
import json
import logging

url = "https://www.instagram.com/api/v1/media/3567131323569705648/likers/"

# Define the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",  # Automatically accepts compressed responses
    "X-CSRFToken": "8VUPjiUh6f0PsnIjOGiIH0",
    "X-IG-App-ID": "936619743392459",
    "X-ASBD-ID": "129477",
    "X-IG-WWW-Claim": "hmac.AR1Xz_ywrmFEWg9tAlsQAsXKobwAjYkuzkZhbfPwOkkeZtPr",
    "X-Web-Session-ID": "71vg3a:e5v45a:pluq37",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://www.instagram.com/p/DGA_woQipKw/",
    "Cookie": "csrftoken=8VUPjiUh6f0PsnIjOGiIH0; ds_user_id=72329672386; wd=1366x450; datr=q2qjZ6rHqa4ijSXFLA35CG9U; mid=Z6b80wALAAF1Th9n7Nib0BLud9b4; ig_did=C0133D3A-B5C5-4BDB-8A3E-54A5D57C3BF9; ps_l=1; ps_n=1; sessionid=72329672386%3AfXIsjYrYTrF9WZ%3A4%3AAYeyENWiehs3GpnhzrYdTtBSsUvtGA__YJpkcfJYHA; rur=\\\"RVA,72329672386,1771077095:01f74af4aeb48686ab42d9193da8504dd8742f66169a5dcdbf966b0173def7a657c214f8\\\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "TE": "trailers"
}

# Make the request
response = requests.get(url, headers=headers)

# Check if the response is successful (status code 200)
if response.status_code == 200:
    try:
        # Try parsing the response as JSON
        data = response.json()
        response_text = response.text  # Get raw text
        # Save the response JSON to a file
        with open("likers.json", "w", encoding="utf-8") as json_file:
            json.dump(response.json(), json_file, indent=4, ensure_ascii=False)
        
        print("Response saved to liker.json")
    
    except json.JSONDecodeError:
        print("Failed to parse JSON. Saving raw response as text.")
        with open("liker_response.txt", "w", encoding="utf-8") as file:
            file.write(response.text)
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print("Response content:", response.text)  # Print raw content for debugging