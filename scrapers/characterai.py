import requests
import json
import os
import time
import random

# Use up-to-date token!
def get_token():
    token = "Token 9443a6fb1927b0acaa251ab25a3e75717d23680a"
    return token

# Make sure to use up-to-date cookie!
def get_cookie():
    #cookie = "_gcl_au=1.1.1239282306.1692981331; _gid=GA1.2.1732984568.1693680763; _legacy_auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true; auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZHZkc2hhdzEyMy4iLCIiXV0:1qcpeF:lHg70ewHQCyxs4N0X9I9txqFHsH9YeAkTi3BzS-TnOk; sessionid=3a9e6xopso0vvz1cen3vmf7c7hvwr7ef; csrftoken=j12eSqfpJp9PHJksWpvWd4Qc6GsaKPAc; __cuid=80f0a08c6bec47f48384c3a34c3e39be; amp_fef1e8=3cb0be49-aee7-4be9-8fba-a6c4fef00cccR...1h9e178qo.1h9e18p6b.7.0.7; cf_clearance=9auVkuHdBSgcNRzSSKF1urdlWjshF_mhJk_mF8NMisc-1693804022-0-1-511a64bf.115f2b6c.61b3b5f-0.2.1693804022; __cf_bm=HH5FpCzjEqperE_bj9BdMKWqDUxaViYNyydVCoS5Gaw-1693805295-0-ARlNgrAjtyxidjCuJIAvI+WBjXoRi96WWOdxI4xhOZtu4Uc11QpDGk+dJzt7gLOpblpE9u4C8AFMEI36+kCBPjg=; _gat=1; _ga=GA1.1.564753635.1692154906; _ga_VG80HET2CQ=GS1.1.1693801129.8.1.1693805301.54.0.0; __cfwaitingroom=ChhBZlk4Ylh5Z1JhdWtHL3BWWVRxb293PT0SrAIyc1gwbGFXMzM4dWxFbGtyMzdOYWxuVWJLNXNTT2RJNksvR08vSVR3SXNDdjBxWnJPMXdvOEVUMC9OdytiS1VoUGlrK0lESVdVc3VzQU9SREFkS2F1S0lxeVVyUzBQbVBMVGY5UGI2alJZL2RVRHpVbHdvb3BETUU3NDlyaXU1ZmROVytDVEZjQXd0NGthWUVYM3o2U0h3Q0MwcWxpZXFFbVBkUGhMenlrKzRHREZnTjUya3JJOGhwbHZRcTBYcHlTc2M0VW9MYjFBZllMNVBHY2Mrc3NmdXFGaHZwOFVkUU0wUDJvUTRLUUdnRVU4QUExblovVkpObldZVFZYdFNCci96MmVDN2EwaWttTlFnTkVGMlBkN2QvVGFLZm5CMGRTRUR2WlFTRmFCMD0%3D"
    cookie = "_gcl_au=1.1.1239282306.1692981331; _gid=GA1.2.1732984568.1693680763; _legacy_auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true; auth0.dyD3gE281MqgISG7FuIXYhL2WEknqZzv.is.authenticated=true; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZHZkc2hhdzEyMy4iLCIiXV0:1qcpeF:lHg70ewHQCyxs4N0X9I9txqFHsH9YeAkTi3BzS-TnOk; sessionid=3a9e6xopso0vvz1cen3vmf7c7hvwr7ef; csrftoken=j12eSqfpJp9PHJksWpvWd4Qc6GsaKPAc; __cuid=80f0a08c6bec47f48384c3a34c3e39be; amp_fef1e8=3cb0be49-aee7-4be9-8fba-a6c4fef00cccR...1h9e178qo.1h9e18p6b.7.0.7; cf_clearance=QpMfrKlqmPCAJwGRi9tnOmtiff8w1g2pK.UCPXQ95cc-1693806138-0-1-511a64bf.b723e8ef.61b3b5f-0.2.1693806138; __cf_bm=6_pXbtBxMaZSWdd3VnlJCAy8zvTM6nEVmAref6i7CZU-1693807811-0-AS/xj0ffVVmnFE3PGQLtN++fa3GM9qc6T4xftswwLmIgCsj8THuoGdarBd36AR/+j8p3OEDXeRercev+yuJzYWc=; _ga_VG80HET2CQ=GS1.1.1693801129.8.1.1693807813.59.0.0; _ga=GA1.1.564753635.1692154906; _gat=1; __cfwaitingroom=Chh3M2kyY0N5Nk1GMTk4YUxDTFJIVEJnPT0SrAJHQmtMeGFpa29BQnBMbkljbHo4R2VMSFRiRVMyc2F5SjIydG84VzJNRC9keXJRSXg3Q05Qb3VrQjJIT2loYzlGYmFiZ3FLajZTSlZLbnZCL1ZrS2pmbjZpYWR6MkNNVEh1aHRJUG1KaUFUc3hLWUVYRHJSSUlwVlZscUtjcUhlOTVvSURubTUxdjZpeXRRM3lndnN3VWo5dENOVUVFRnJGV205UmdUR1Mybmc1bUhWbjhZSHdJc2lKb2ZMalpWTGVvdENRRzBQYWNST2o5c1JDQkF5Qk4xUG9BU3FCaEJLbHRTdjdYUXFXZ0xLZEpCTXVESUVUVFpLRFlQSFVQTEZWaGJ2YXFXcDVmU2hSMVozMnNFTUJGR2JKd2M4RUlVRi8zV3BFK3NxeVBwMD0%3D"
    return cookie

# Chars by category
def scrape_characterai_chars_by_category():
    url = 'https://beta.character.ai/chat/curated_categories/characters/'

    token = get_token()
    cookie = get_cookie()
    headers = {
                "Authorization": token,
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

    try:
        response = requests.get(url, headers=headers)
        print("Response:", response)
        response.raise_for_status()
        print("Response text: ", response.text)

        response_json = response.json()

        current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_file_path = "./characterai_data/characterai_chars_by_category.json"
        absolute_file_path = os.path.join(current_directory, relative_file_path)

        if os.path.exists(absolute_file_path):
            with open(absolute_file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.append(response_json)
        
        with open(absolute_file_path, "w") as f:
            json.dump(existing_data, f)
        
        print("Done getting chars by category")
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    return 

# Get char info
def scrape_char_info(char_id):
    url = f"https://beta.character.ai/chat/character/"
    token = get_token()
    cookie = get_cookie()
    headers = {
                "Authorization": token,
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
    
    data = {
        "external_id": char_id,
    }

    time.sleep(random.random()*2)

    try:
        response = requests.post(url, headers=headers, json=data)
        print("Response:", response)
        response.raise_for_status()

        response_json = response.json()
        
        current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_file_path = "./characterai_data/characterai_chars.json"
        absolute_file_path = os.path.join(current_directory, relative_file_path)

        if os.path.exists(absolute_file_path):
            with open(absolute_file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.append(response_json)
        
        with open(absolute_file_path, "w") as f:
            json.dump(existing_data, f)
        
        print(f"Done getting char_id = {char_id}")
        print("Len of existing data:", len(existing_data))

    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    return 

def get_all_char_infos():
    file_path = "./character_data/characterai_chars_by_category.json"
    absolute_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)

    with open(absolute_file_path, "r") as f:
        data = json.load(f)

    for category in data["characters_by_curated_category"]:
        for char in data["characters_by_curated_category"][category]:
            char_id = char["external_id"]
            scrape_char_info(char_id)
    return 

if __name__ == "__main__":
    #char_id = "OkQhIQ0WNko1Wx-phdqhUFI0vV3NLIpC8L6Ryyz2-Xo"
    #char_id = "aBOwEZHooxA-puwaqdKbgU5NJ-BNns-FrLGlQNB8794"
    #scrape_characterai()
    #scrape_char_info(char_id)
    #get_all_char_infos()
    scrape_characterai_chars_by_category()
    