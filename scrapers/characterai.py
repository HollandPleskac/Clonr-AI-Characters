import requests
import json
import os
import time
import random


def get_token():
    token = "Token 9443a6fb1927b0acaa251ab25a3e75717d23680a"
    return token

def get_cookie():
    cookie = "_legacy_auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true; auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true;sessionid=3a9e6xopso0vvz1cen3vmf7c7hvwr7ef;csrftoken=j12eSqfpJp9PHJksWpvWd4Qc6GsaKPAc;"
    return cookie

def scrape_characterai():
    #url = "https://beta.character.ai"
    url = 'https://beta.character.ai/chat/curated_categories/characters/'

    token = get_token()
    cookie = get_cookie()
    headers = {
                "Authorization": "Bearer " + token,
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

    try:
        response = requests.get(url, headers=headers)
        print("Response:", response)
        response.raise_for_status()
        print("Response text: ", response.text)
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    return 

def scrape_char_info(char_id):
    url = f"https://beta.character.ai/chat/character/info/{char_id}"
    token = get_token()
    cookie = get_cookie()
    headers = {
                "Authorization": "Bearer " + token,
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

    try:
        response = requests.get(url, headers=headers)
        print("Response:", response)
        response.raise_for_status()
        print("Response text: ", response.text)
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    return 

if __name__ == "__main__":
    scrape_characterai()