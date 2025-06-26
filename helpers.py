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
import csv

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
            ygo_pro_api = fetch_json_data(f'https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes&language={language_code}')
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
    name = name_checker(name, "Maliss <P> March Hare", "Maliss P March Hare")
    name = name_checker(name, "Maliss <P> White Rabbit", "Maliss P White Rabbit")
    name = name_checker(name, "Maliss <P> Chessy Cat", "Maliss P Chessy Cat")
    name = name_checker(name, "Maliss <P> Dormouse", "Maliss P Dormouse")
    name = name_checker(name, "Maliss <Q> Red Ransom", "Maliss Q Red Ransom")
    name = name_checker(name, "Maliss <Q> White Binder", "Maliss Q White Binder")
    name = name_checker(name, "Maliss <Q> Hearts Crypter", "Maliss Q Hearts Crypter")
    name = name_checker(name, "Maliss <C> MTP-07", "Maliss C MTP-07")
    name = name_checker(name, "Maliss <C> GWC-06", "Maliss C GWC-06")
    name = name_checker(name, "Maliss <C> TB-11", "Maliss C TB-11")

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

    ##  For Debugging
    # safe_filename = re.sub(r'[\\/*?:"<>|]', "_", deck_info_link) + ".html"
    # with open(safe_filename, "wb") as f:
    #     f.write(deck_url.content)

    soup_deck = BeautifulSoup(deck_url.content, "html.parser")  # Pass through html parser
    # card_elements = soup_deck.find_all("div", class_="t_row c_normal open")  # Find all card structures
    card_elements = soup_deck.select("div.t_row.c_normal.open")
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
    if isinstance(list, str):
        return list
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

def load_local_database(filename="yugioh_card_database.json"):
    """
    Loads the aggregated card database from a JSON file.
    Returns a dictionary of card data or an empty dictionary if not found.
    """
    if not os.path.exists(filename):
        print(f"Warning: Local database '{filename}' not found. Will perform a full scrape.")
        return {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"Successfully loaded local database from '{filename}'.")
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'. File might be corrupt.")
        return {}
    except Exception as e:
        print(f"An error occurred while loading the local database: {e}")
        return {}


def populate_card_from_db(card_obj, db_entry):
    """
    Populates a Card structure from a dictionary entry from our local DB,
    correctly mapping JSON keys to the Card class attributes.
    """
    # Map the keys from the JSON file to the Card class attributes.
    # Use .get() to prevent errors if a key is missing from the JSON entry.
    card_obj.name = db_entry.get("name", "")
    card_obj.attribute = db_entry.get("attribute", "")
    card_obj.link = db_entry.get("link", "")
    card_obj.link_arrows = db_entry.get("link_arrows", "")
    card_obj.rank = db_entry.get("rank", "")
    card_obj.level = db_entry.get("level", "")
    card_obj.attack = db_entry.get("attack", "")
    card_obj.defense = db_entry.get("defense", "")
    card_obj.type = db_entry.get("type", "")
    card_obj.spell_attribute = db_entry.get("spell_attribute", "")
    card_obj.summoning_condition = db_entry.get("summoning_condition", "")
    card_obj.card_text = db_entry.get("card_text", "")
    card_obj.card_supports = db_entry.get("card_supports", "")
    card_obj.card_anti_supports = db_entry.get("card_anti_supports", "")
    card_obj.card_actions = db_entry.get("card_actions", "")
    card_obj.effect_types = db_entry.get("effect_types", "")

    # Handle attributes with different names between JSON and Card class
    card_obj.pend_scale = db_entry.get("pendulum_scale", "")
    card_obj.pend_effect = db_entry.get("pendulum_condition", "")
    card_obj.card_passcode = db_entry.get("passcode", "")
    card_obj.card_status = db_entry.get("status", "")

    # Note: 'race', and 'archetype' are not in the base CSV,
    # so they will remain as their default empty values from the Card's __init__.

    return card_obj


def extract_card_info_yugipedia(soup: BeautifulSoup) -> dict:
    """
    Extracts detailed information for a Yu-Gi-Oh! card from its Yugipedia page.

    This function parses a BeautifulSoup object of a card's Yugipedia page HTML
    to retrieve key details like card type, attributes, stats, prices, and
    translations.

    Args:
        soup: A BeautifulSoup object containing the parsed HTML of the card page.

    Returns:
        A dictionary containing the extracted card information. Fields for which
        no data could be found will be empty (e.g., '', [], {}).
        The structure of the returned dictionary is as follows:
        {
            'card_type': str,
            'attribute': str,
            'types': list[str],
            'level': str,
            'atk_def': str,
            'password': str,
            'effect_types': list[str],
            'status': list[str],
            'tcgplayer_prices': list[dict],
            'other_languages': dict
        }
    """
    # Initialize a dictionary to hold the card data with default empty values.
    card_data = {
        'card_type': '',
        'attribute': '',
        'types': [],
        'level': '',
        'atk_def': '',
        'password': '',
        'effect_types': [],
        'status': [],
        'tcgplayer_prices': [],
        'other_languages': {}
    }

    # --- 1. Extract Main Card Info from the infobox ---
    try:
        # # for debugging
        # with open("fetched_page.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())

        # The main card details are in a table with the class 'innertable'.
        info_table = soup.find('table', class_='innertable')
        if info_table:
            # Iterate over each row (tr) in the table to find the data.
            for row in info_table.find_all('tr'):
                header = row.find('th')
                value_cell = row.find('td')
                if not header or not value_cell:
                    continue

                header_text = header.get_text(strip=True)
                
                # Based on the header, extract the corresponding data.
                if header_text == 'Card type':
                    card_data['card_type'] = value_cell.get_text(strip=True)
                elif header_text == 'Attribute':
                    card_data['attribute'] = value_cell.get_text(strip=True)
                elif header_text == 'Types':
                    # Types are separated by ' / ', so we split them into a list.
                    types_text = value_cell.get_text(strip=True)
                    card_data['types'] = [t.strip() for t in types_text.split('/')]
                elif header_text == 'Level':
                    card_data['level'] = value_cell.get_text(strip=True)
                elif header_text == 'ATK/DEF':
                    card_data['atk_def'] = value_cell.get_text(strip=True)
                elif header_text == 'Password':
                    card_data['password'] = value_cell.get_text(strip=True)
                elif header_text == 'Effect types':
                    # Effect types are in a list, so we get each list item.
                    card_data['effect_types'] = [li.get_text(strip=True) for li in value_cell.find_all('li')]
                elif header_text == 'Status':
                    # Each status is in its own div.
                    card_data['status'] = [div.get_text(strip=True) for div in value_cell.find_all('div', class_=True)]
    except Exception:
        # In case of any error during parsing, we pass and return the defaults.
        pass

    # --- 3. Extract Other Languages ---
    try:
        # Find the "Other languages" section header.
        lang_header = soup.find('span', class_='mw-headline', id='Other_languages')
        if lang_header:
            # The language table is the next sibling of the header's parent (h2).
            lang_table = lang_header.find_parent('h2').find_next_sibling('table', class_='wikitable')
            if lang_table:
                # Use an iterator to handle the special case for Japanese (2 rows).
                row_iter = iter(lang_table.find('tbody').find_all('tr'))
                next(row_iter, None)  # Skip the header row of the language table.

                for row in row_iter:
                    lang_th = row.find('th')
                    cells = row.find_all('td')

                    if not lang_th or len(cells) < 2:
                        continue
                    
                    lang = lang_th.get_text(strip=True)
                    name = cells[0].get_text(strip=True)
                    
                    # Replace <br> tags with newlines to preserve formatting in card text.
                    for br in cells[1].find_all('br'):
                        br.replace_with('\n')
                    text = cells[1].get_text(strip=False).strip()
                    
                    entry = {'name': name, 'text': text}

                    # Handle the special case for Japanese, which has a separate row for Romaji.
                    if lang == 'Japanese':
                        # Peek at the next row in the HTML to check for the Romaji name.
                        next_row = row.find_next_sibling('tr')
                        if next_row and not next_row.find('th'):
                            romaji_cell = next_row.find('td', {'lang': 'ja-Latn'})
                            if romaji_cell:
                                entry['romaji'] = romaji_cell.get_text(strip=True)
                                # Consume the Romaji row from our iterator so we don't process it again.
                                next(row_iter, None)
                    
                    card_data['other_languages'][lang] = entry
    except Exception:
        pass

    return card_data