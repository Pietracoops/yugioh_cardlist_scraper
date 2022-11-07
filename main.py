import os
import pathlib
import requests
from bs4 import BeautifulSoup
import card_structure
import helpers
import copy


script_dir = pathlib.Path(__file__).parent.resolve()

delimiter = '$'
output_path = pathlib.PurePath(script_dir, "data", "output")
base_URL = "https://www.db.yugioh-card.com"
URL = "https://www.db.yugioh-card.com/yugiohdb/card_list.action"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)

# Initialization
list_of_cards = []
count = 0

pack_elements = soup.find_all("div", class_="pack pack_en")
link_elements = soup.find_all("input", class_="link_value")
pack_names = soup.find_all('div', class_="pack")


for element in link_elements:   # Loop through Packs
    # If the count exceeds number of names - Exit
    if count >= len(pack_names):
        break

    # Get name of the Pack from the pack HTML array
    pack_name = pack_names[count].text.strip()
    pack_name = pack_name.split('\n')   # Split according to the new line character
    if len(pack_name) != 0:             # If the split found a new character line, grab only the first part
        pack_name = pack_name[0]
    print(pack_name)
    count += 1  # Increase the count for next iteration

    pack_name = helpers.cleanStr(pack_name,  [("/", "-"), (":", "-")])
    if os.path.isfile(f"{output_path}/{pack_name}.csv"):
        print(f"Skipping {count} of {len(pack_names)}")
        continue

    deck_info_link = element['value']   # Get the link for each individual pack
    deck_url = requests.get(base_URL + deck_info_link)  # Request the URL containing the card lists
    soup_deck = BeautifulSoup(deck_url.content, "html.parser")  # Pass through html parser
    card_elements = soup_deck.find_all("div", class_="t_row c_normal")  # Find all card structures

    # Looping through all the cards on the page
    card_count = 0
    for card_info in card_elements:
        card_count += 1
        print(f"{count} of {len(pack_names)} : card {card_count} of {len(card_elements)}")
        tmp_card = card_structure.Card()

        name = card_info.find_all("span", class_="card_name")
        tmp_card.name = name[0].text

        attribute = card_info.find_all("span", class_="box_card_attribute")
        attribute = helpers.cleanStr(attribute[0].text, [("\n", "")])
        tmp_card.attribute = attribute

        # Monster card specific information
        if not 'SPELL' in attribute and not 'TRAP' in attribute:
            level = card_info.find_all("span", class_="box_card_level_rank level")
            if len(level) != 0:
                level = helpers.cleanStr(level[0].text, [("\n", "")])
                tmp_card.level = level

            link = card_info.find_all("span", class_="box_card_linkmarker")
            if len(link) != 0:
                link = helpers.cleanStr(link[0].text, [("\n", "")])
                tmp_card.link = link

            card_type = card_info.find_all("span", class_="card_info_species_and_other_item")
            card_type = helpers.cleanStr(card_type[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
            tmp_card.type = card_type

            attack_power = card_info.find_all("span", class_="atk_power")
            attack_power = helpers.cleanStr(attack_power[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
            tmp_card.attack = attack_power

            def_power = card_info.find_all("span", class_="def_power")
            def_power = helpers.cleanStr(def_power[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
            tmp_card.defense = def_power

        # Spell and Trap card specific information
        if 'SPELL' in attribute or 'TRAP' in attribute:
            spell_attribute = card_info.find_all("span", class_="box_card_effect")
            if len(spell_attribute) != 0:
                spell_attribute = helpers.cleanStr(spell_attribute[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
                tmp_card.spell_attribute = spell_attribute

        card_text = card_info.find_all("dd", class_="box_card_text c_text flex_1")
        card_text = helpers.cleanStr(card_text[0].text, [("\n", ""), ("\t", ""), ("\r", "")])
        tmp_card.card_text = card_text

        # Store the card structure into the list of cards
        list_of_cards.append(copy.copy(tmp_card))
        tmp_card.clear()    # Clear the individual temporary structure for next card

    helpers.outputCSV(f"{output_path}/{pack_name}.csv", list_of_cards, delimiter)
    list_of_cards.clear()   # Reset list for the next pack

print("DONE")
