import requests
import json
import os
import time
import random

def get_jwt():
    endpoint = "https://clerk.charstar.ai/v1/client/sessions/sess_2Us57vyMB2kFyXF1LBwcaiDB5nu/tokens?_clerk_js_version=4.56.2"
    # Go in console and find network req for tokens?_clerk_js_version=...
    cookie = "__client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yVXM0aFh4Z2kyR0JYNXFtemdoeGNPcnNtRWoiLCJyb3RhdGluZ190b2tlbiI6Im5ldTJiYm5nNm1lcnB6d3gxYWZqb242cWd0eWVxbGxnZGpycG5jejgifQ.Z9DGHTfuwHOhwUDK3QGZum9sJTsysfftZFLlaCoTIxuYWUqzsQdqxokqjH7MSGTXw-b5qYdUv81mI3PJEuUWNTrk2RCD_QAWD8Kl6NzA1lq-euMaLxumicmttX34qPJdAQ6iwwNkEVwURX9WZpxo503A7k2n5NwD6QuiKO3WAlF3pmAosIDZZVRw4quNqsnryXldSNtlq3UIzAaZjWGOqC05c4Hum7fogO2_1aO_ILHFK7RB7_XeXjPpT4nFJr1553iqBmv5XJdUFJrrPOpG4zgyJiUf9bciG1inAw_rFGSDA0qe0oIv7bHp7Q6qcqbdaaCv0ESQIPB6F8t5qI3GDw;__client_uat=1693715284"
    headers = {
        "Cookie": cookie,
    }
    response = requests.post(endpoint, headers=headers)
    print(response.json())
    return response.json()['jwt']

# Get chars 
def scrape_charstarai_chars(nsfw=False):
    jwt = get_jwt()
    i = 0
    while True:
        if nsfw:
            url = f"https://charstar.ai/api/bots/explore?sort=TOP&nsfw=true&page={i}"
        else:
            url = f"https://charstar.ai/api/bots/explore?sort=TOP&nsfw=false&page={i}"
        
        try:
            time.sleep(random.random()*3)

            headers = {
                "Authorization": "Bearer " + jwt,
                "Cookie": "__session=" + jwt,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            res_json = response.json()
            print("res json:", res_json)
            res_headers = response.headers
            print("res headers:", res_headers)
            char_data_list = res_json["bots"]

            if len(char_data_list) == 0:
                return

            current_directory = os.path.dirname(os.path.abspath(__file__))
            if nsfw:
                relative_file_path = "./charstar_data/charstarai_chars_nsfw.json"
            else:
                relative_file_path = "./charstar_data/charstarai_chars_sfw.json"
            absolute_file_path = os.path.join(current_directory, relative_file_path)
            if os.path.exists(absolute_file_path):
                with open(absolute_file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            existing_data.extend(char_data_list)

            with open(absolute_file_path, "w") as f:
                json.dump(existing_data, f)
            
            i += 1
            print(f"Done running page = {i}")
            print("Len of existing data:", len(existing_data))
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            if response.status_code == 401:
                print("401 error, getting new jwt")
                jwt = get_jwt()
            else:
                break
    return 

# Get char info (more detailed)
def scrape_charstarai_chars_info(nsfw=False):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    if nsfw:
        relative_file_path = "./charstar_data/charstarai_chars_nsfw.json"
    else:
        relative_file_path = "./charstar_data/charstarai_chars_sfw.json"
    absolute_file_path = os.path.join(current_directory, relative_file_path)
    with open(absolute_file_path, "r") as f:
        existing_data = json.load(f)
    
    bot_ids = [bot["id"] for bot in existing_data]
    print(f"Fetching {len(bot_ids)} bot_ids")

    jwt = get_jwt()

    i = 0

    while i < len(bot_ids): 
        url = f'https://charstar.ai/api/bots/{bot_ids[i]}/info'
        
        try:
            time.sleep(random.random()*3)
            headers = {
                "Authorization": "Bearer " + jwt,
                "Cookie": "__session=" + jwt,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            res_json = response.json()
            res_headers = response.headers

            current_directory = os.path.dirname(os.path.abspath(__file__))
            if nsfw:
                relative_file_path = "./charstar_data/charstarai_chars_nsfw_info.json"
            else:
                relative_file_path = "./charstar_data/charstarai_chars_sfw_info.json"
            absolute_file_path = os.path.join(current_directory, relative_file_path)
            if os.path.exists(absolute_file_path):
                with open(absolute_file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            existing_data.append(res_json)

            with open(absolute_file_path, "w") as f:
                json.dump(existing_data, f)
            
            i += 1
            print(f"Done running char info page = {i}")
            print("Len of existing char info data:", len(existing_data))
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            if response.status_code == 401:
                print("401 error, getting new jwt")
                jwt = get_jwt()
            else:
                break
    return


if __name__ == "__main__":
    #scrape_charstarai_chars(nsfw=True)
    scrape_charstarai_chars_info(nsfw=True)
    #get_token()