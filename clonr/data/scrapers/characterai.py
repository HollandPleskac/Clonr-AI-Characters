import requests
import json
import os
from bs4 import BeautifulSoup

def extract_character_info_via_api(char_id, token):
    url = "https://beta.character.ai/chat/character/info/"
    # example char_id: qtEICpGfFS8f5Zr5kCHR1EsGsHlawNutYSZJq_IEZDY
    # example token: ?
    payload = {
        'external_id': char_id
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Token " + token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None

def extract_all_character_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    character_elements = soup.find_all("div", class_="character-slide-card-v3")

    characters_info = {}
    for character_element in character_elements:
        name_element = character_element.find("div", style="font-size: 14px; font-weight: bold;")
        description_element = character_element.find("div", style="font-size: 12px; max-width: 100%;")
        username_element = character_element.find("div", class_="username-truncated")

        if name_element and description_element and username_element:
            name = name_element.text.strip()
            description = description_element.text.strip()
            username = username_element.find("div").text.strip()

            characters_info[name] = {
                "description": description,
                "username": username,
            }

    return characters_info

def scrape_characterai():
    url = "https://beta.character.ai"

    try:
        response = requests.get(url)
        chars_info = extract_all_character_info(response.text)
        print("Characters info:", chars_info)
        for character, info in chars_info.items():
            print(f"Character: {character}")
            print(f"Description: {info['description']}")
            print(f"Username: {info['username']}")
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    return 

# Found via: https://beta.character.ai/chat/curated_categories/characters/
def parse_results():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    relative_file_path = "results.json"
    absolute_file_path = os.path.join(current_directory, relative_file_path)
    sorted_results = []
    with open(absolute_file_path, "r") as f:
        data = json.load(f)
        categories = data['characters_by_curated_category'].keys()
        characters_by_category = data['characters_by_curated_category']

        for category, characters in characters_by_category.items():
            for character in characters:
                character['character_category'] = category
                sorted_results.append(character)
        
        sorted_results = sorted(sorted_results, key=lambda k: k['participant__num_interactions'], reverse=True)
        
        for i in range(min(len(sorted_results), 10)):
            print(sorted_results[i])
         
    return sorted_results