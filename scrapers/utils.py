
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_char_url(char_name, char_wiki):
    modified_char_name = char_name.replace(" ", "_")
    try:
        base_url = f"https://{char_wiki}.fandom.com/{modified_char_name}"
        response = requests.get(base_url)
        response.raise_for_status()
        if response.status_code == 200:
            return base_url
    except requests.exceptions.RequestException as e:
        print("Error fetching the webpage:", e)
        return None
    return None

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

char_name = "Yae Miko"
char_wiki = "genshin-impact"
base_url = find_char_url(char_name, char_wiki)

# base_url = "https://chainsaw-man.fandom.com/wiki/Makima"
# base_url = 'https://genshin-impact.fandom.com/'
# base_url = 'https://genshin-impact.fandom.com/wiki/Yae_Miko'

found_links = find_links_with_same_base_url(base_url)
print("Links on the webpage that contain the original webpage URL:")
for link in found_links:
    print(link)