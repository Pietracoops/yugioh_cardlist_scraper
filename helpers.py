import re

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
