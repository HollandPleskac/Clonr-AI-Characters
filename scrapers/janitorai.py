import requests
import json
import os
import time


def scrape_janitorai():
    for i in range(1, 32):
        url = f"https://miguel.janitorai.com/characters?page={i}&search=neighbor&mode=all&sort=popular"
        
        try:
            time.sleep(1)
            # headers = {
            #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            # }
            response = requests.get(url)
            response.raise_for_status() 

            res_json = response.json()
            char_data_list = res_json["data"]

            current_directory = os.path.dirname(os.path.abspath(__file__))
            relative_file_path = "janitorai_chars.json"
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
    scrape_janitorai()