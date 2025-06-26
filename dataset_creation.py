import os
import csv
import json

# --- Configuration ---
# The folder where your CSV pack files are located.
# The script assumes this folder is in the same directory as the script itself.
CSV_DIRECTORY = "data/en" 

# The name of the final output JSON file.
OUTPUT_FILENAME = "yugioh_card_database.json"

# Define the headers based on your CSV structure. This is crucial for mapping.
HEADERS = [
    "passcode", "name", "status", "attribute", "type", "link", "link_arrows",
    "rank", "pendulum_scale", "level", "attack", "defense", "spell_attribute",
    "summoning_condition", "pendulum_condition", "card_text", "card_supports",
    "card_anti_supports", "card_actions", "effect_types"
]

def create_yugioh_dataset():
    """
    Reads all CSV files from a directory, aggregates card data,
    and writes it to a single JSON file.
    """
    card_database = {} # This will store our final aggregated data.

    print(f"Starting to process CSV files from '{CSV_DIRECTORY}'...")

    # Check if the directory exists
    if not os.path.isdir(CSV_DIRECTORY):
        print(f"Error: Directory '{CSV_DIRECTORY}' not found.")
        print("Please create the folder and place your CSV files inside it.")
        return

    # Get a list of all CSV files in the directory
    csv_files = [f for f in os.listdir(CSV_DIRECTORY) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in '{CSV_DIRECTORY}'.")
        return

    for filename in csv_files:
        # Extract the pack name from the filename (e.g., "Pharaohs_Servant.csv" -> "Pharaohs_Servant")
        pack_name = os.path.splitext(filename)[0]
        print(f"  -> Processing pack: {pack_name}")

        file_path = os.path.join(CSV_DIRECTORY, filename)

        try:
            with open(file_path, mode='r', encoding='utf-8') as infile:
                # Use the csv reader with '$' as the delimiter
                reader = csv.reader(infile, delimiter='$')
                
                for row in reader:
                    # Skip empty rows or rows that don't match the expected column count
                    if not row or row[0].lower() in HEADERS:
                        continue

                    card_name = row[1] # The 'Name' is the second column (index 1)

                    # If this is the first time we've seen this card
                    if card_name not in card_database:
                        # Create a dictionary for the card's data by zipping headers and row data
                        card_info = dict(zip(HEADERS, row))
                        
                        # Add the new 'packs' field
                        card_info["packs"] = [pack_name]
                        
                        # Add the complete card entry to our main database
                        card_database[card_name] = card_info
                    
                    # If the card already exists, just add the new pack to its list
                    else:
                        # Check to avoid adding duplicate pack names for the same card (just in case)
                        if pack_name not in card_database[card_name]["packs"]:
                            card_database[card_name]["packs"].append(pack_name)

        except Exception as e:
            print(f"      Error processing file {filename}: {e}")

    # Write the final aggregated data to a JSON file
    print(f"\nAggregation complete. Found {len(card_database)} unique cards.")
    print(f"Writing data to '{OUTPUT_FILENAME}'...")

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as outfile:
        # Use indent=4 for a human-readable, pretty-printed JSON file
        json.dump(card_database, outfile, indent=4, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    create_yugioh_dataset()