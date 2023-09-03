import requests
import json
import os
import time
import random

def get_token():
    token = "eyJhbGciOiJIUzI1NiIsImtpZCI6ImIxTENVc09BZkpaZVlCd3AiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNjkzNzYyNTQ2LCJpYXQiOjE2OTM3NTUzNDYsImlzcyI6Imh0dHBzOi8vbWNtenh0em9tbXBueGt5bmRkYm8uc3VwYWJhc2UuY28vYXV0aC92MSIsInN1YiI6IjFmZWM1NjEyLWE1OGMtNGFhYi1iMGI2LTE5OTA3YWQ0MzczMCIsImVtYWlsIjoiZHZkc2hhdzEyM0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImdvb2dsZSIsImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQWNIVHRlNEt4ZFVxbno4NU5BUzIxR3FCa2ZhODZCOEtpYmdUUDduS1hhbS02VGE9czk2LWMiLCJlbWFpbCI6ImR2ZHNoYXcxMjNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6IkRhdmlkIFNoYXciLCJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYW1lIjoiRGF2aWQgU2hhdyIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQWNIVHRlNEt4ZFVxbno4NU5BUzIxR3FCa2ZhODZCOEtpYmdUUDduS1hhbS02VGE9czk2LWMiLCJwcm92aWRlcl9pZCI6IjExNDcwNzM1OTM2ODQ3MjI1OTIwNiIsInN1YiI6IjExNDcwNzM1OTM2ODQ3MjI1OTIwNiJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im9hdXRoIiwidGltZXN0YW1wIjoxNjkyMTU0ODc3fV0sInNlc3Npb25faWQiOiI0ZmQzZjQ2Yi0yYWMwLTQ0MjUtODEwMS1jNmRmZWY0MTA3YWMifQ.kJ7eJx4_d7uXt3fkas17KKnAL5WH-CRM_kgLgzsygQQ"
    return token 

def scrape_janitorai_chars():
    token = get_token()
    for i in range(0, 1):
        url = f"https://miguel.janitorai.com/characters?page={i}&search=neighbor&mode=all&sort=popular"
        
        try:
            time.sleep(random.random()*3)
            headers = {
                "Authorization": f"Bearer {token}",
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            res_json = response.json()
            char_data_list = res_json["data"]

            current_directory = os.path.dirname(os.path.abspath(__file__))
            relative_file_path = "./janitor_data/janitorai_chars.json"
            absolute_file_path = os.path.join(current_directory, relative_file_path)

            if os.path.exists(absolute_file_path):
                with open(absolute_file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            existing_data.extend(char_data_list)

            with open(absolute_file_path, "w") as f:
                json.dump(existing_data, f)

        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
    return 

def scrape_janitorai_chars_info():
    token = get_token()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    relative_file_path = "./janitor_data/janitorai_chars.json"
    absolute_file_path = os.path.join(current_directory, relative_file_path)
    with open(absolute_file_path, "r") as f:
        existing_data = json.load(f)
    
    bot_ids = [bot["id"] for bot in existing_data]
    print(f"Fetching {len(bot_ids)} bot_ids")

    for i in range(0, len(bot_ids)):
        bot_id = bot_ids[i]
        url = f"https://miguel.janitorai.com/characters/{bot_id}"
        
        try:
            time.sleep(random.random()*3)
            headers = {
                "Authorization": f"Bearer {token}",
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            res_json = response.json()
            char_data_list = res_json["data"]

            current_directory = os.path.dirname(os.path.abspath(__file__))
            relative_file_path = "./janitor_data/janitorai_chars.json"
            absolute_file_path = os.path.join(current_directory, relative_file_path)

            if os.path.exists(absolute_file_path):
                with open(absolute_file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            existing_data.extend(char_data_list)

            with open(absolute_file_path, "w") as f:
                json.dump(existing_data, f)

        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
    return


if __name__ == "__main__":
    scrape_janitorai_chars()