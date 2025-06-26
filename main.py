import os
import pathlib
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import card_structure
import helpers
import copy
import re
from alive_progress import alive_bar
from langdetect import detect
import time
import argparse
import sys

YGOPRODECK_API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

link_dict = {1: "Bottom-Left",
             2: "Bottom",
             3: "Bottom-Right",
             4: "Left",
             6: "Right",
             7: "Top-Left",
             8: "Top",
             9: "Top-Right"}

if __name__ == "__main__":

    # ARGUMENTS PARSING #
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--language", action="store", type=str,
                        choices=["en", "fr", "ja", "de", "it", "es", "pt", "ko"],
                        default="en",
                        help="Select the generation language")
    parser.add_argument("-f", "--fast", action='store_true', default=False)
    parser.add_argument("-db", "--local_database", action='store_true', default=False)

    args = parser.parse_args()
    ###########################

    script_dir = pathlib.Path(__file__).parent.resolve()
    
    # Check Platform
    helpers.check_platform()

    # Load our generated JSON database into memory to reduce scrapes
    local_card_db = helpers.load_local_database("yugioh_card_database.json")

    # Clone the yugioh-card-history git
    repository_url = 'https://github.com/db-ygorganization-com/yugioh-card-history.git'
    clone_repo_path = pathlib.PurePath(script_dir, "yugioh-card-history")
    helpers.clone_or_pull_repo(repository_url, str(clone_repo_path))

    # English="en", French="fr", Japanese="ja", Deutsch="de", Italian="it", Spanish="es", Portugese = "pt", Korean="ko"
    language_code = args.language
    scrape_additional_data = not args.fast

    # Get the language database
    file_pattern = pathlib.PurePath(script_dir, "yugioh-card-history", language_code, "*.json")
    card_hashmap = helpers.combine_json_files(str(file_pattern), language_code, 'name')
    card_en_id_hashmap = helpers.combine_json_files(str(file_pattern), 'en', 'id')

    delimiter = '$'
    output_path = pathlib.PurePath(script_dir, "data", language_code)
    wiki_URL = "https://yugioh.fandom.com/wiki/"
    yugipedia_URL = "https://yugipedia.com/wiki/"
    base_URL = "https://www.db.yugioh-card.com"
    URL = f"https://www.db.yugioh-card.com/yugiohdb/card_list.action??clm=1&wname=CardSearch&request_locale={language_code}"

    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)

    # Initiate a session and update the headers.
    requests_session = requests.session()
    headers = {
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    requests_session.headers.update(headers)

    # Initialization
    list_of_cards = []
    processed_card_database = {}
    count = 0
    pack_elements, link_elements, pack_names = helpers.get_packs_and_links(URL, requests_session)

    with alive_bar(len(link_elements), dual_line=True, title='Packs Processed', force_tty=True) as bar:

        for element_num in range(len(link_elements)):   # Loop through Packs
            # If the count exceeds number of names - Exit
            if count >= len(pack_names):
                break

            # Get name of the Pack from the pack HTML array
            pack_name = helpers.get_pack_name(pack_names, count)
            count += 1  # Increase the count for next iteration

            if os.path.isfile(f"{output_path}/{pack_name}.csv"):
                bar()
                continue

            # Get the link for each individual pack
            card_elements, raw_url1 = helpers.get_card_elements(base_URL, link_elements[element_num], language_code, requests_session)

            bar.text = f'-> Processing pack: {pack_name}, please wait...'

            # Looping through all the cards on the page
            card_count = 0
            for card_info in card_elements:
                card_count += 1
                tmp_card = card_structure.Card()
                name = card_info.find_all("span", class_="card_name")
                card_name_text = helpers.cleanStr(name[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                tmp_card.name = card_name_text

                if args.local_database:
                    if card_name_text in local_card_db:
                        bar.text = f'-> Found in local DB: {card_name_text}'
                        db_entry = local_card_db[card_name_text]
                        tmp_card = helpers.populate_card_from_db(tmp_card, db_entry)
                        
                        list_of_cards.append(copy.copy(tmp_card))
                        processed_card_database[card_name_text] = copy.copy(tmp_card) # Also update in-run cache
                        tmp_card.clear()
                        continue # Skip to the next card in the pack

                if card_name_text in processed_card_database:
                    list_of_cards.append(copy.copy(processed_card_database[card_name_text]))
                    continue
                
                # #Uncomment this code if you need to debug a certain card
                # if name[0].text == "Enemy Controller":
                #     print("e")

                card_start_time = time.time()

                card_hash_data = card_hashmap.get(name[0].text)
                process_english_name = False
                if card_hash_data != None:

                    if card_hash_data.get('localizedAttribute') != None:
                        tmp_card.attribute = card_hash_data.get('localizedAttribute')
                    elif card_hash_data.get('attribute') != None:
                        tmp_card.attribute = card_hash_data.get('attribute')
                    elif card_hash_data.get('frameType') != None:
                        tmp_card.attribute = card_hash_data.get('frameType').upper()

                    if card_hash_data.get('englishAttribute') == "trap" \
                        or card_hash_data.get('frameType') == "trap" \
                        or card_hash_data.get('englishAttribute') == "spell" \
                        or card_hash_data.get('frameType') == "spell":
                        if card_hash_data.get('localizedProperty') != None:
                            tmp_card.spell_attribute = card_hash_data.get('localizedProperty')
                        elif card_hash_data.get('race') != None:
                            tmp_card.spell_attribute = card_hash_data.get('race')
                        if card_hash_data.get('desc') != None:
                            tmp_card.card_text = card_hash_data.get('desc').replace('\r\n', ' ').replace('\n', ' ')
                        else:
                            tmp_card.card_text = card_hash_data.get('effectText').replace('\r\n', ' ').replace('\n', ' ')
                    else: # It's a monster
                        if card_hash_data.get('level') != None:
                            tmp_card.level = card_hash_data.get('level')
                        if card_hash_data.get('rank') != None:
                            tmp_card.rank = card_hash_data.get('rank')
                        if card_hash_data.get('linkRating') != None:
                            tmp_card.link = card_hash_data.get('linkRating')
                        elif card_hash_data.get('linkval') != None:
                            tmp_card.link = card_hash_data.get('linkval')
                        if card_hash_data.get('linkArrows') != None:
                            tmp_card.link_arrows = '/'.join(
                                [link_dict[int(key)] for key in card_hash_data.get('linkArrows')])
                            tmp_card.link_arrows = tmp_card.link_arrows.split('/')
                        elif card_hash_data.get('linkmarkers') != None:
                            tmp_card.link_arrows = card_hash_data.get('linkmarkers')
                        if card_hash_data.get('pendScale') != None:
                            tmp_card.pend_scale = card_hash_data.get('pendScale')
                        elif card_hash_data.get('scale') != None:
                            tmp_card.pend_scale = card_hash_data.get('scale')

                        if tmp_card.pend_scale != "":
                            if card_hash_data.get('pendEffect') != None:
                                tmp_card.pend_effect = card_hash_data.get('pendEffect')
                                tmp_card.card_text = card_hash_data.get('effectText')
                            elif card_hash_data.get('desc') != None:
                                pattern = r"\[ Pendulum Effect \](.*?)\[ Monster Effect \](.*?)$"
                                matches = re.search(pattern, card_hash_data.get('desc'), re.DOTALL)
                                if matches:
                                    tmp_card.pend_effect = matches.group(1).replace('\n', '').replace('\r', '')
                                    if '\n' in matches.group(2):
                                        tmp_card.summoning_condition = matches.group(2).split('\n')[0].replace('\r', '')
                                        tmp_card.card_text = matches.group(2).split('\n')[1]
                                    else:
                                        tmp_card.card_text = matches.group(2).replace('\r', '').replace('\n', '')
                        elif card_hash_data.get('desc') != None:
                            if '\n' in card_hash_data.get('desc'):
                                tmp_card.summoning_condition = card_hash_data.get('desc').split('\n')[0].replace('\r', '')
                                tmp_card.card_text = card_hash_data.get('desc').split('\n')[1].replace('\n', '').replace('\r', '')
                            else:
                                tmp_card.card_text = card_hash_data.get('desc').replace('\n', '').replace('\r', '')

                        if card_hash_data.get('properties') != None:
                            tmp_card.type = '/'.join(card_hash_data.get('properties'))
                        else:
                            tmp_card.type = f"[{card_hash_data.get('race')}/{card_hash_data.get('frameType')}]"
                        if card_hash_data.get('atk') != None:
                            tmp_card.attack = card_hash_data.get('atk')
                        if card_hash_data.get('def') != None:
                            tmp_card.defense = card_hash_data.get('def')
                        if card_hash_data.get('effectText') != None and '\n' in card_hash_data.get('effectText'):
                            tmp_card.summoning_condition = card_hash_data.get('effectText').split('\n')[0]


                    # Use the konami code to find other information in ygoprodeck api
                    try:
                        en_hashmap_data = card_en_id_hashmap.get(card_hash_data.get('misc_info')[0].get('konami_id'))
                    except:
                        en_hashmap_data = None

                    if en_hashmap_data != None:
                        if en_hashmap_data.get('name') != None:
                            tmp_card.card_passcode = en_hashmap_data.get('id')
                        english_name = en_hashmap_data.get('name')
                    else:
                        process_english_name = True
                else:
                    process_english_name = True

                if process_english_name == True:

                    if language_code != "en":
                        link_value_struct = card_info.find_all("input", class_="link_value")
                        link_value = link_value_struct[0].attrs['value']

                        card_info_page, card_raw_url = helpers.get_page(base_URL + link_value, language_code, requests_session)
                        try:
                            english_name = card_info_page.find("div", {"id": "cardname"}).h1
                            english_name = english_name.select_one("span").text
                        except:
                            continue

                        if len(english_name) > 2:
                            if detect(english_name) != 'en':
                                continue

                    else:
                        english_name = tmp_card.name

                    attribute = card_info.find_all("span", class_="box_card_attribute")
                    attribute = helpers.cleanStr(attribute[0].text, [("\n", "")])
                    tmp_card.attribute = attribute

                    # Monster card specific information
                    # Exemption list is missing japanese and korean so will not work for those two languages and will probably crash
                    exemption_list = ['SPELL', 'TRAP', 'MAGIE', 'PIÈGE', 'ZAUBER', 'FALLE', 'MAGIA', 'TRAPPOLA', 'MÁGICA', 'TRAMPA', 'ARMADILHA', 'MAGIA', '魔法', '罠', '마법', '함정']
                    monster_card_found = True
                    for pattern in exemption_list:
                        if re.search(pattern, attribute):
                            monster_card_found = False

                    if monster_card_found:
                        level = card_info.find_all("span", class_="box_card_level_rank level")
                        if len(level) != 0:
                            level = helpers.cleanStr(level[0].text, [("Level ", ""), ("\n", "")])
                            tmp_card.level = level

                        rank = card_info.find_all("span", class_="box_card_level_rank rank")
                        if len(rank) != 0:
                            rank = helpers.cleanStr(rank[0].text, [("Rank ", ""), ("\n", "")])
                            tmp_card.rank = rank

                        link = card_info.find_all("span", class_="box_card_linkmarker")
                        if len(link) != 0:
                            link = helpers.cleanStr(link[0].text, [("Link ", ""), ("\n", "")])
                            tmp_card.link = link

                        card_type = card_info.find_all("span", class_="card_info_species_and_other_item")
                        card_type = helpers.cleanStr(card_type[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                        tmp_card.type = card_type

                        if re.search('Pendulum', card_type):
                            pend_scale = card_info.find_all("span", class_="box_card_pen_scale")
                            pend_scale = helpers.cleanStr(pend_scale[0].text, [("P Scale ", ""), ("\n", ""), ("\t", ""), ("\r", "")])
                            tmp_card.pend_scale = pend_scale

                            pend_effect = card_info.find_all("span", class_="box_card_pen_effect c_text flex_1")
                            pend_effect = helpers.cleanStr(pend_effect[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                            tmp_card.pend_effect = pend_effect

                        attack_power = card_info.find_all("span", class_="atk_power")
                        attack_power = helpers.cleanStr(attack_power[0].text, [("ATK ", ""), ("\n", ""), ("\t", ""), ("\r", "")])
                        tmp_card.attack = attack_power

                        def_power = card_info.find_all("span", class_="def_power")
                        def_power = helpers.cleanStr(def_power[0].text, [("DEF ", ""), ("\n", ""), ("\t", ""), ("\r", "")])
                        tmp_card.defense = def_power

                    # Spell and Trap card specific information
                    if re.search('SPELL', attribute) or re.search('TRAP', attribute):
                        spell_attribute = card_info.find_all("span", class_="box_card_effect")
                        if len(spell_attribute) != 0:
                            spell_attribute = helpers.cleanStr(spell_attribute[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                            tmp_card.spell_attribute = spell_attribute

                    card_text = card_info.find_all("dd", class_="box_card_text c_text flex_1")
                    if len(card_text[0].contents) > 1 and ("Fusion" in tmp_card.type or "Synchro" in tmp_card.type
                                                            or "Xyz" in tmp_card.type or "Link" in tmp_card.type):
                        summoning_condition = helpers.cleanStr(card_text[0].contents[0], [("\n", ""), ("\t", ""), ("\r", "")])
                        new_card_text = ""
                        for i in range(1, len(card_text[0].contents)):
                            if isinstance(card_text[0].contents[i], Tag):
                                continue
                            new_card_text += helpers.cleanStr(card_text[0].contents[i], [("\n", ""), ("\t", ""), ("\r", "")])
                        card_text = new_card_text
                    else:
                        summoning_condition = ""
                        card_text = helpers.cleanStr(card_text[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                    tmp_card.summoning_condition = summoning_condition
                    tmp_card.card_text = card_text

                # Grab additional Card information from the wiki

                extra_info_time_start = time.time()
                if scrape_additional_data:
                    # Yugioh Wiki
                    processed_card_name = helpers.process_english_name(english_name)
                    debug_url = wiki_URL + processed_card_name
                    card_url = requests_session.get(wiki_URL + processed_card_name)  # Request the URL containing the card lists
                    if card_url.status_code != 200:
                        print(f"error occured for card {tmp_card.name} : {english_name}: url: {debug_url}")
                    soup_deck = BeautifulSoup(card_url.content, "html.parser")  # Pass through html parser
                    ind_card_elements = soup_deck.find_all("tr", class_="cardtablerow")  # Find all card structures

                    if card_url.status_code == 200 and len(ind_card_elements) == 0:
                        # We'll try specifying (card) in the name
                        card_url = requests_session.get(wiki_URL + processed_card_name + "_(card)")  # Request the URL containing the card lists
                        soup_deck = BeautifulSoup(card_url.content, "html.parser")  # Pass through html parser
                        ind_card_elements = soup_deck.find_all("tr", class_="cardtablerow")  # Find all card structures
                        if len(ind_card_elements) == 0:
                            print(f"error occured for card {tmp_card.name} : {english_name} - failed with (card): url: {debug_url}")

                    for ind_card_info in ind_card_elements:

                        if re.search('Passcode', ind_card_info.text):
                            lists = ind_card_info.find_all("td", class_="cardtablerowdata")
                            if len(lists) != 0:
                                passcode = lists[0]
                                tmp_card.card_passcode = helpers.cleanStr(passcode.text, [("\n", ""), ("\t", ""), ("\r", "")])

                        if re.search('Link Arrows', ind_card_info.text):
                            lists = ind_card_info.find_all("td", class_="cardtablerowdata")
                            if len(lists) != 0:
                                card_arrows = lists[0]
                                arrows = []
                                for arrow in card_arrows:
                                    if not isinstance(arrow, NavigableString) and arrow.text != '':
                                        arrows.append(arrow.text)
                                tmp_card.link_arrows = arrows

                        if re.search('Card effect types', ind_card_info.text):
                            lists = ind_card_info.find_all("td", class_="cardtablerowdata")
                            if len(lists) != 0:
                                card_effect_types = lists[0]
                                effect_types = []
                                for effect_type in card_effect_types:
                                    if not isinstance(effect_type, NavigableString) and effect_type.text != '\n':
                                        for effect in effect_type:
                                            if effect.text not in effect_types and not re.search('\n', effect.text):
                                                effect_types.append(effect.text)
                                tmp_card.effect_types = effect_types

                        if re.search('Statuses', ind_card_info.text):
                            lists = ind_card_info.find_all("td", class_="cardtablerowdata")
                            if len(lists) != 0:
                                card_status = lists[0]
                                tmp_card.card_status = helpers.cleanStr(card_status.text, [(" ", "")])

                        if re.search('Card search categories', ind_card_info.text):
                            lists = ind_card_info.find_all("div", class_="hlist")
                            for row_list in lists:
                                if re.search('Supports', row_list.text):
                                    card_supports = []
                                    card_search_categories = row_list.contents[1]
                                    for support in card_search_categories:
                                        if not '\n' in support.text and support.text != 'Supports ':
                                            card_supports.append(support.text)
                                    tmp_card.card_supports = card_supports

                                if re.search('Anti-supports', row_list.text):
                                    card_anti_supports = []
                                    card_search_categories = row_list.contents[1]
                                    for anti_support in card_search_categories:
                                        if not '\n' in anti_support.text and anti_support.text != 'Anti-supports ':
                                            card_anti_supports.append(anti_support.text)
                                    tmp_card.card_anti_supports = card_anti_supports

                                if re.search('Actions', row_list.text):
                                    card_actions = []
                                    card_search_categories = row_list.contents[1]
                                    for action in card_search_categories:
                                        if not re.search('\n', action.text) and action.text != 'Actions ':
                                            card_actions.append(action.text)
                                    tmp_card.card_actions = card_actions


                    # Yugipedia
                    processed_card_name = helpers.process_english_name(english_name)
                    debug_url = yugipedia_URL + processed_card_name
                    card_url = requests_session.get(yugipedia_URL + processed_card_name)  # Request the URL containing the card lists

                    if card_url.status_code != 200:
                        print(f"error occured for card {tmp_card.name} : {english_name}: url: {debug_url}")
                    soup_deck = BeautifulSoup(card_url.content, "html.parser")  # Pass through html parser
                    card_info = helpers.extract_card_info_yugipedia(soup_deck)

                    card_class = card_info.get('card_type', 'N/A')
                    if tmp_card.attribute == '':
                        attribute = card_info.get('attribute', 'N/A')

                    # if tmp_card.level == '':
                    #     level = card_info.get('level', 'N/A')
                    
                    # card_atk, card_def = card_info.get('atk_def', 'N/A').split('/')
                    # if tmp_card.attack == '':
                    #     tmp_card.attack = card_atk
                    # if tmp_card.defense == '':
                    #     tmp_card.defense = card_def
                    
                    if tmp_card.card_passcode == '':
                        tmp_card.card_passcode = card_info.get('password', 'N/A')
                    
                    if tmp_card.type == '':
                        card_types = card_info.get('types', [])
                    if tmp_card.effect_types == '':
                        tmp_card.effect_types = card_info.get('effect_types', [])
                    tmp_card.card_status = '/'.join(card_info.get('status', []))
                    tmp_card.other_languages = card_info.get('other_languages', {})


                    # print("Other Languages:")
                    # # Use .items() to get both the language (key) and its details (value)
                    # for lang, details in card_info.get('other_languages', {}).items():
                    #     lang_name = details.get('name', 'N/A')
                    #     lang_text = details.get('text', 'N/A').replace('\n', ' ') # Replace newlines for cleaner printing
                    #     print(f"  Language: {lang}")
                    #     print(f"    Name: {lang_name}")
                    #     # For Japanese, check if a Romaji name exists
                    #     if 'romaji' in details:
                    #         print(f"    Romaji: {details['romaji']}")
                    #     # print(f"    Text: {lang_text[:50]}...") # Print first 50 chars of text
                    # print("-" * 20)
                    
                card_end_time = time.time()
                #print(f"Card Process Time: {card_end_time - card_start_time} - Extra Info Time: {card_end_time - extra_info_time_start}")
                bar.text = f'-> Processing pack: {pack_name}, {tmp_card.name}'


                # Store the card structure into the list of cards
                list_of_cards.append(copy.copy(tmp_card))
                processed_card_database[tmp_card.name] = copy.copy(tmp_card)
                tmp_card.clear()    # Clear the individual temporary structure for next card

            helpers.outputCSV(f"{output_path}/{pack_name}.csv", list_of_cards, delimiter)
            list_of_cards.clear()   # Reset list for the next pack
            bar()
    print("DONE")
