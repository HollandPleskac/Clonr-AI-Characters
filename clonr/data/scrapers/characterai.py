import requests
import json
import os
import guidance
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from clonr.data.parsers import FandomParser
from clonr.data.parsers import WikiQuotesParser

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

def generate_example_quotes(char_name, char_title, char_greeting, char_category):
    load_dotenv()

    example_quotes = """
    {{#system~}}
    You are a helpful AI assistant that can generate character profiles.
    {{~/system}}
    {{#user~}}
    Please answer the following questions to generate a character profile based on the given information.

    Here is the name of the character: {{char_name}}

    Here is the title of the character: {{char_title}}

    Here is an example greeting of the character: {{char_greeting}}

    Here is the category of the character: {{char_category}}

    Could you produce five example quotes that the character would say?

    {{~/user}}
    {{#assistant~}}
    {{gen 'result' temperature=0.1 max_tokens=1000}}
    {{~/assistant}}
    """

    gpt_turbo = guidance.llms.OpenAI('gpt-3.5-turbo', api_key=os.getenv('OPENAI_API_KEY'))
    char_name = 'Raiden Shogun and Ei'
    char_title = 'From Genshin Impact'
    char_greeting = 'Shogun: No salutations needed. My exalted status shall not be disclosed as we travel among the common folk. I acknowledge that you are a person of superior ability. Henceforth, you will be my guard. Worry not. Should any danger arise, I shall dispose of it.'
    char_category = 'Anime Game Characters'
    example_quotes = guidance(example_quotes, llm=gpt_turbo)

    result = example_quotes(char_name=char_name, char_title=char_title, char_greeting=char_greeting, char_category=char_category)
    print(result)
    return result

def generate_character_profile(char_data):
    char_title = char_data['title']
    char_name = char_data['participant__name']
    char_greeting = char_data['greeting']
    char_category = char_data['character_category']
    print("This is char_name: ", char_name)
    if 'from' in char_title.lower():
        char_wiki = char_title.lower().split("from ")[1]
        char_wiki = char_wiki.replace(" ", "-")
    else:
        return 
    print("This is char_wiki: ", char_wiki)
    fandom_parser = FandomParser()
    fandom_content = None
    try:
        fandom_result = fandom_parser.extract(char_name, char_wiki)
        fandom_content = fandom_result.content
    except Exception as e:
        print("Cannot get Fandom result: ", e)

    wikiquotes_parser = WikiQuotesParser()
    wikiquotes_content = None
    try:
        wikiquotes_result = wikiquotes_parser.extract(char_name)
        wikiquotes_content = wikiquotes_result.content
    except Exception as e:
        print("Cannot get WikiQuotes result: ", e)

    if wikiquotes_content is None:
        print("Generating synthetic quotes..")
        #generate_example_quotes()

    return {
        fandom_content: fandom_content,
        wikiquotes_content: wikiquotes_content
    }
