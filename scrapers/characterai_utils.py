import requests
import json
import os
import io
import guidance
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from clonr.data.parsers import FullURLParser, FandomParser
from clonr.data.parsers import WikiQuotesParser
from clonr.data.parsers import WikipediaParser
from .utils import find_links_with_same_base_url
#from PIL import Image
#from google.cloud import storage

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

def get_token():
    token = "Token 9443a6fb1927b0acaa251ab25a3e75717d23680a"
    return token

def scrape_characterai():
    #url = "https://beta.character.ai"
    url = 'https://beta.character.ai/chat/curated_categories/characters/'

    token = get_token()
    headers = {
                "Authorization": "Bearer " + token,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }

    try:
        response = requests.get(url, headers=headers)
        print("Response:", response)
        response.raise_for_status()
        print("RESPONSE TEXT: ", response.text)
        #chars_info = extract_all_character_info(response.text)
        #print("Characters info:", chars_info)
        # for character, info in chars_info.items():
        #     print(f"Character: {character}")
        #     print(f"Description: {info['description']}")
        #     print(f"Username: {info['username']}")
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

# def download_webp_image(image_url: str) -> Image.Image:
#     response = requests.get(image_url)
#     response.raise_for_status() 
#     return Image.open(io.BytesIO(response.content))

# def upload_to_gcs(file_data: bytes, filename: str, content_type: str):
#     bucket_name = "TODO"
#     client = storage.Client()
#     bucket = client.get_bucket(bucket_name)
#     blob = bucket.blob(filename)
#     #content_type='image/webp'
#     blob.upload_from_string(file_data, content_type=content_type)
#     return

def generate_character_profile(char_data):
    char_title = char_data['title']
    char_name = char_data['participant__name']
    char_greeting = char_data['greeting']
    char_category = char_data['character_category']
    avatar_file_name = char_data['avatar_file_name']

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
    
    img_prefix = 'https://characterai.io/i/80/static/avatars/'
    img = None
    
    # try:
    #     img = download_webp_image(img_prefix + avatar_file_name)
    # except Exception as e:
    #     print("Cannot download image: ", e)

    return {
        fandom_content: fandom_content,
        wikiquotes_content: wikiquotes_content,
        img: img,
    }

## NEW FLOW - FANDOM 

def find_links_with_same_base_url(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the webpage:", e)
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    p = urlparse(base_url)
    page_domain = p.scheme + "://" + p.netloc + p.path

    links = []
    for link in soup.find_all('a', href=True):
        link_url = link['href']
        full_url = urljoin(base_url, link_url)

        # Check if the full_url contains the original webpage domain
        if full_url.startswith(page_domain):
            p = urlparse(full_url)
            if not p.params and not p.query and '#' not in full_url:
                links.append(full_url)

    return sorted(set(links))

def find_char_url(char_name, char_wiki):
    modified_char_name = char_name.replace(" ", "_")
    try:
        base_url = f"https://{char_wiki}.fandom.com/wiki/{modified_char_name}"
        response = requests.get(base_url)
        response.raise_for_status()
        if response.status_code == 200:
            return base_url
    except requests.exceptions.RequestException as e:
        print("Error fetching the webpage:", e)
        return None
    return None

def extract_quotes_from_url(parser, url):
    fandom_result = parser.extract(url)
    if fandom_result:
        return fandom_result.content
    else:
        return None

def get_all_example_dialogues(char_name, char_wiki, parser):
    char_url = find_char_url(char_name, char_wiki)
    results = []
    if char_url:
        found_links = find_links_with_same_base_url(char_url)
        print("Links on the webpage that contain the original webpage URL:")
        print(found_links)
        for found_link in found_links:
            print("Processing link: ", found_link)
            result = extract_quotes_from_url(parser, found_link)
            if result:
                results.append(result)
    
    results = "\n\n".join(results)

    if len(results) < 100:
        print("No results found for this character.")
        return None

    file_path = f'clonr/data/examples/{char_name}_{char_wiki}.txt'

    if not os.path.exists(file_path):
        with open(file_path, 'x') as f:
            f.write(results)
    else:
        print(f"File '{file_path}' already exists. Won't overwrite.")
    return results

parser = FullURLParser()

results = parse_results()

for result in results:
    char_name = result['participant__name']
    char_title = result['title']
    char_wiki = ''
    if 'from' in char_title.lower():
        char_wiki = char_title.lower().split("from ")[1]
        char_wiki = char_wiki.replace(" ", "-").strip('.').strip('!')
    if 'of' in char_title.lower():
        char_wiki = char_title.lower().split("of")[1].strip("of ")
        char_wiki = char_wiki.replace(" ", "-").strip('.').strip('!')
    
    if char_wiki == '':
        continue 

    print(f"Processing char_name = {char_name}, char_wiki = {char_wiki}")
    total_results = get_all_example_dialogues(char_name, char_wiki, parser)
