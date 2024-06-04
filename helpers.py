import re
import platform
import git
import os
import json
import glob
import copy
import requests
from card_structure import Card
from bs4 import BeautifulSoup

def fetch_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print('Failed to fetch JSON data. Status code:', response.status_code)
        return None
def combine_json_files(file_pattern, language_code, id):
    output_hashmap = {}

    # Find all JSON files matching the given file pattern
    json_files = glob.glob(file_pattern)

    if language_code == "en" or language_code == "fr" or language_code == "de" or language_code == "it" or language_code == "pt":
        if language_code != "en":
            ygo_pro_api = fetch_json_data(f'https://db.ygoprodeck.com/api/v7/cardinfo.php??misc=yes&language={language_code}')
        else:
            ygo_pro_api = fetch_json_data(f'https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes')
        #output_hashmap = {item['misc_info'][0]['konami_id']: item for item in ygo_pro_api['data']}
        count = 0
        for item in ygo_pro_api['data']:
            if id == 'name':
                output_hashmap[item['name']] = item
            else:
                if item['misc_info'][0].get('konami_id') != None:
                    output_hashmap[item['misc_info'][0]['konami_id']] = item
                else:
                    count += 1

        # Languages can only be queried on cardinfo.php and must be passed with &language= along with the language code.
        # The language codes are: fr for French, de for German, it for Italian and pt for Portuguese.
    else:

        # Read and combine the contents of each JSON file CARD
        for file in json_files:
            with open(file, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                output_hashmap[data.get(id)] = data

    return output_hashmap

def clone_or_pull_repo(url, destination):
    if os.path.exists(destination):
        repo = git.Repo(destination)
        repo.remotes.origin.pull()
        print(f"Updating {destination} - this may take a couple of minutes... ", end='')
    else:
        print(f"Cloning {url} - this may take a couple of minutes... ", end='')
        git.Repo.clone_from(url, destination)
    print("Done")

def check_platform():
    current_platform = platform.system()
    if current_platform == 'Linux':
        print('Running on Linux')
    elif current_platform == 'Windows':
        print('Running on Windows')
    else:
        print('Running on', current_platform)
    return current_platform


def name_checker(name, find_name, change_name):
    '''
    Checks if name is equivalent to the find_name, and swaps it with change_name
    Attributes :
    - name:  Input string [ string ]
    - find_name:  String to find [ string ]
    - change_name:  String to swap in [ string ]

    Outputs :
    - name: Processed card name [ string ]

    '''
    if name == find_name:
        name = change_name
    return name

def apply_name_exceptions(name):
    '''
    Applies exceptions in card names, whether these are typos or improper website conventions
    Attributes :
    - name:  Raw english card name [ string ]

    Outputs :
    - name: Processed english card name [ string ]

    '''
    # If other exceptions are found, simply place the conversion here.
    name = name_checker(name, "Apophis the Swamp Deity", "Aphophis the Swamp Deity")
    name = name_checker(name, "Tally-ho! Springans", "Tally-Ho! Springans")
    name = name_checker(name, "Terrors of the Overroot", "Terrors of the Overrroot")
    name = name_checker(name, "Protector of The Agents - Moon", "Protector of the Agents - Moon")
    name = name_checker(name, "Kaiser Glider - Golden Burst", "Kaiser Glider Golden Burst")
    name = name_checker(name, "Zektrike Kou-ou", "Zektrike Kou-Ou")
    name = name_checker(name, "Double Disruptor Dragon", "Double Disrupter Dragon")
    name = name_checker(name, "Floowandereeze and the Unexplored Winds", "Floowandereeze and the Unexplored Wind")
    name = name_checker(name, "Vampiric Koala (Updated from: Vampire Koala)", "Vampiric Koala")
    name = name_checker(name, "Vampiric Orchis (Updated from: Vampire Orchis)", "Vampiric Orchis")
    name = name_checker(name, "Amazoness Archer (Updated from: Amazon Archer)", "Amazoness Archer")
    name = name_checker(name, "Darklord Nurse Reficule (Updated from: Nurse Reficule the Fallen One)", "Darklord Nurse Reficule")
    name = name_checker(name, "Darklord Marie (Updated from: Marie the Fallen One)", "Darklord Marie")
    name = name_checker(name, "Black Skull Dragon (Updated from: B. Skull Dragon)", "Black Skull Dragon")
    name = name_checker(name, "Malefic Red-Eyes Black Dragon (Updated from: Malefic Red-Eyes B. Dragon)", "Malefic Red-Eyes Black Dragon")
    name = name_checker(name, "Darkfall (Updated from: Dark Trap Hole)", "Darkfall")
    name = name_checker(name, "Silent Graveyard (Updated from: Forbidden Graveyard)", "Silent Graveyard")
    name = name_checker(name, "Armityle the Chaos Phantasm (Updated from: Armityle the Chaos Phantom)", "Armityle the Chaos Phantasm")
    name = name_checker(name, "Supernatural Regeneration (Updated from: Metaphysical Regeneration)", "Supernatural Regeneration")
    name = name_checker(name, "Wattkid (Updated from: Oscillo Hero #2)", "Wattkid")
    name = name_checker(name, "Hidden Spellbook (Updated from: Hidden Book of Spell)", "Hidden Spellbook")
    name = name_checker(name, "Dark Scorpion - Cliff the Trap Remover (Updated from: Cliff the Trap Remover)", "Dark Scorpion - Cliff the Trap Remover")
    name = name_checker(name, "Spellbook Organization (Updated from: Pigeonholing Books of Spell)", "Spellbook Organization")
    name = name_checker(name, "Muko (Updated from: Null and Void)", "Muko")
    name = name_checker(name, "Vampire Baby (Updated from: Red-Moon Baby)", "Vampire Baby")
    name = name_checker(name, "Sky Scout (Updated from: Harpie's Brother)", "Sky Scout")
    name = name_checker(name, "Cipher Soldier (Updated from: Kinetic Soldier)", "Cipher Soldier")
    name = name_checker(name, "B.E.S. Big Core (Updated from: Big Core)", "B.E.S. Big Core")
    name = name_checker(name, "Slime Toad (Updated from: Frog the Jam)", "Slime Toad")
    name = name_checker(name, "Necrolancer the Time-lord (Updated from: Necrolancer the Timelord)", "Necrolancer the Time-lord")


    return name

def process_english_name(name):
    '''
    Cleans up the english name and prepares it for web page use
    Attributes :
    - name:  Raw english card name [ string ]

    Outputs :
    - name: Processed english card name [ string ]

    '''
    name = apply_name_exceptions(name)
    name = re.sub(' ', '_', name)
    name = re.sub('#', '', name)
    name = re.sub('\?', '%3F', name)  # Need to replace question marks for URL
    name = re.sub('\'', '%27', name)  # Need to replace single quote for URL

    return name


def get_packs_and_links(url, requests_session):
    '''
    Retrieves all card names from card elements array
    Attributes :
    - url:  URL for web page [ string ]
    - requests_session: Requests session object for query usage

    Outputs :
    - pack_elements: HTML array of packs [ string array ]
    - link_elements: HTML array of links [ string array ]
    - pack_names: String array of pack names [ string array ]

    '''
    page = requests_session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    pack_elements = soup.find_all("div", class_="pack pack_en")
    link_elements = soup.find_all("input", class_="link_value")
    pack_names = soup.find_all('div', class_="pack")
    return pack_elements, link_elements, pack_names

def get_card_names(card_elements):
    '''
    Retrieves all card names from card elements array
    Attributes :
    - card_elements:  HTML elements for each individual card in array [ string array ]

    Outputs :
    - name_list: Array of card names [ string ]

    '''
    name_list = []
    for card_info in card_elements:
        name = card_info.find_all("span", class_="card_name")
        name_list.append(name[0].text)
    return name_list

def get_page(base_URL, language_code, requests_session):
    '''
    Retrieves a URL page using requests and beautiful soup
    Attributes :
    - base_URL:  URL for base web page [ string ]
    - language_code: Website language code (e.g. "en") [ string ]
    - requests_session: Requests session object for query usage

    Outputs :
    - soup_deck: HTML output for web page
    - raw_url: The raw URL of the webpage containing the HTML card elements for debugging purposes [ string ]

    '''
    url = requests_session.get(base_URL + f"&request_locale={language_code}")
    raw_url = base_URL + f"&request_locale={language_code}"
    soup_deck = BeautifulSoup(url.content, "html.parser")  # Pass through html parser
    return soup_deck, raw_url

def get_card_elements(base_URL, element, language_code, requests_session):
    '''
    Retrieves the card html elements for a pack
    Attributes :
    - base_URL:  URL for base web page [ string ]
    - element: HTML element containing the deck information
    - language_code: Website language code (e.g. "en") [ string ]
    - requests_session: Requests session object for query usage

    Outputs :
    - card_elements: HTML elements for each individual card in array [ string array ]
    - raw_url: The raw URL of the webpage containing the HTML card elements for debugging purposes [ string ]

    '''
    deck_info_link = element['value']
    deck_url = requests_session.get(base_URL + deck_info_link + f"&request_locale={language_code}")
    raw_url = base_URL + deck_info_link + f"&request_locale={language_code}"
    soup_deck = BeautifulSoup(deck_url.content, "html.parser")  # Pass through html parser
    card_elements = soup_deck.find_all("div", class_="t_row c_normal open")  # Find all card structures
    return card_elements, raw_url

def get_pack_name(pack_names, count):
    '''
    Retrieves the pack name from the pack_names array given a count
    Attributes :
    - pack_names:  Pack name array containing html structure [ string array ]
    - count: Count in array to retrieve pack name from [ int ]

    Outputs :
    - pack_name: Pack name from html structure [ string ]

    '''
    pack_name = pack_names[count].text.strip()
    pack_name = pack_name.split('\n')  # Split according to the new line character
    if len(pack_name) != 0:  # If the split found a new character line, grab only the first part
        pack_name = pack_name[0]
    pack_name = cleanStr(pack_name, [("/", "-"), (":", "-")])
    return pack_name

def cleanStr(str, substitutions):
    '''
    Cleans a string based on a dictionary of strings and their respective substitutions
    Attributes :
    - str:  Input string [ string ]
    - substitutions: Dictionary of substitutions

    Outputs :
    - str: Modified string value after substitutions

    '''
    for pattern, replacement in substitutions:  # Remove patterns that are not of interest
        str = re.sub(pattern, replacement, str)

    return str

def listToStr(list):
    '''
    Combines the elements of a list into a single string
    Attributes :
    - list:  Input list [ string ]

    Outputs :
    - str: string

    '''
    output_string = ""
    for i in range(0, len(list)):
        if i == 0:
            output_string += list[i]
        else:
            output_string += "/" + list[i]

    return output_string

def outputCSV(filename, card_list, delimiter):
    '''
    Outputs the yugioh card list to a CSV file
    Attributes :
    - filename:  File name to output [ string ]
    - card_list: List of yugioh cards in Card structure [ Card ]
    - delimiter: Delimiter to use for file [ char ]

    Outputs :
    - None

    '''

    # Output to csv file the list of cards for the given pack
    f = open(filename, "a", encoding="utf-8")
    # Create the titles
    f.write(f"Passcode{delimiter}Name{delimiter}Status{delimiter}Attribute{delimiter}type{delimiter}link{delimiter}"
            f"link_arrows{delimiter}rank{delimiter}"
            f"pendulum_scale{delimiter}level{delimiter}attack{delimiter}defense{delimiter}spell_attribute"
            f"{delimiter}summoning_condition{delimiter}pendulum_condition{delimiter}card_text{delimiter}"
            f"card_supports{delimiter}card_anti_supports{delimiter}card_actions{delimiter}"
            f"effect_types{delimiter}\n")
    for card in card_list:
        f.write(f"{card.card_passcode}{delimiter}{card.name}{delimiter}"
                f"{card.card_status}{delimiter}{card.attribute}{delimiter}"
                f"{card.type}{delimiter}{card.link}{delimiter}{listToStr(card.link_arrows)}{delimiter}"
                f"{card.rank}{delimiter}{card.pend_scale}{delimiter}"
                f"{card.level}{delimiter}{card.attack}{delimiter}{card.defense}"
                f"{delimiter}{card.spell_attribute}{delimiter}{card.summoning_condition}{delimiter}{card.pend_effect}"
                f"{delimiter}{card.card_text}{delimiter}{listToStr(card.card_supports)}{delimiter}"
                f"{listToStr(card.card_anti_supports)}{delimiter}{listToStr(card.card_actions)}{delimiter}"
                f"{listToStr(card.effect_types)}{delimiter}\n")
    f.close()
