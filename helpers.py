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
    f.write(f"Name{delimiter}Attribute{delimiter}type{delimiter}link{delimiter}rank{delimiter}"
            f"pendulum_scale{delimiter}level{delimiter}attack{delimiter}defense{delimiter}spell_attribute"
            f"{delimiter}summoning_condition{delimiter}pendulum_condition{delimiter}card_text{delimiter}\n")
    for card in card_list:
        f.write(f"{card.name}{delimiter}{card.attribute}{delimiter}"
                f"{card.type}{delimiter}{card.link}{delimiter}{card.rank}{delimiter}{card.pend_scale}{delimiter}"
                f"{card.level}{delimiter}{card.attack}{delimiter}{card.defense}"
                f"{delimiter}{card.spell_attribute}{delimiter}{card.summoning_condition}{delimiter}{card.pend_effect}"
                f"{delimiter}{card.card_text}{delimiter}\n")
    f.close()
