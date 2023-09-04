import requests
import json
import os
import time
import random

algolia_endpoint = "https://gb3bhh57fj-dsn.algolia.net/1/indexes/*/queries"

headers = {
    "x-algolia-api-key": 'ae643249c50806bfbd20dc02ab6a0401',
    "x-algolia-application-id": 'GB3BHH57FJ',
}

def scrape_spicychat_chars():
    is_processing = True 
    page = 0
    while is_processing:
        time.sleep(random.random()*3)

        try:
            data = {
                "requests": [
                    {
                        "indexName": "characters",
                        "params": f"facetFilters=%5B%5B%22is_nsfw%3Afalse%22%5D%5D&facets=%5B%22is_nsfw%22%2C%22tags%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=48&maxValuesPerFacet=100&page={page}&query=&tagFilters=",
                    },
                    # {
                    #     "indexName": "characters",
                    #     "params": "analytics=false&clickAnalytics=false&facets=is_nsfw&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=0&maxValuesPerFacet=100&page=0&query=",
                    # },
                ],
            }
            response = requests.post(algolia_endpoint, json=data, headers=headers)
            response.raise_for_status()
            results = response.json()["results"]
            hits = results[0]["hits"]

            if len(hits) == 0:
                is_processing = False
                print("Done processing spicychat, page is: ", page)
                return
            
            current_directory = os.path.dirname(os.path.abspath(__file__))
            relative_file_path = "./spicychat_data/spicychat_chars.json"
            absolute_file_path = os.path.join(current_directory, relative_file_path)

            if os.path.exists(absolute_file_path):
                with open(absolute_file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            existing_data.extend(hits)
            
            with open(absolute_file_path, "w") as f:
                json.dump(existing_data, f)
            
            print(f"Done getting page = {page}")
            print("Len of existing data:", len(existing_data))

            page += 1

        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
    return 

if __name__ == "__main__":
    scrape_spicychat_chars()
