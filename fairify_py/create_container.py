# Creates Dockerfile from information in RTE and Model Cards

# Get relevent cards from user input (ViT, DistilBERT, or Whisper) and either build or infer

# Use card information to create a new Dockerfile

import yaml
import requests

# Get YAML Cards from Github 

# Example with distilBERT, but can be changed to other rte, model, or datasets
RTE_CARD_URL = 'https://raw.githubusercontent.com/RobQuickIU/FAIRify/main/cards/FAIR_cards/distilbert_rte.yaml'
MODEL_CARD_URL = 'https://raw.githubusercontent.com/RobQuickIU/FAIRify/main/cards/FAIR_cards/distilbert-base-uncased.yaml'
DATA_CARD_URL = 'https://raw.githubusercontent.com/RobQuickIU/FAIRify/main/cards/FAIR_cards/wikitext-2-raw-v1.yaml'
OUTPUT_FILE = 'Dockerfile_Createed'

# Read Card
def read_card(url):
    try:
        print(f"Attempting Card download from: {url}")
        response = requests.get(url)

        response.raise_for_status()

        card_content = response.text

        #DEBUG
        #print("\n--- RAW CONTENT RECEIVED ---")
        #print(card_content[:500]) # Print first 500 characters
        #print("----------------------------\n")

        data = yaml.safe_load(card_content)
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or connecting to {url}: {e}")
        return None

    except yaml.YAMLError as e:
        print(f"Error parsing YAML from {url}: {e}")
      
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Write Card to File
def write_card(filepath, content):
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        print(f"\nSuccessfully wrote combined data to *{filepath}*")
    except Exception as e:
        print(f"An error occurred while writing to {filepath}: {e}")

# Read Cards
rte_card = read_card(RTE_CARD_URL)
model_card = read_card(MODEL_CARD_URL)
data_card = read_card(DATA_CARD_URL)

# Set Container Core Environment
# Get RTE Data
core_name = rte_card['system_stack']['core-language']
core_version = rte_card['system_stack']['core-language_version']

# Get Model Data
package_list = model_card.get('additional-packages', [])
executable = model_card['executables']['build']

# Write Out File
with open(OUTPUT_FILE, 'w') as f:
    # Core System Install
    print("FROM " + core_name + ":" + str(core_version), file=f)

    # Set Virtual Environment
    print("WORKDIR /app", file=f)
    print("ENV VIRTUAL_ENV=/opt/venv", file=f)
    print("RUN python -m venv $VIRTUAL_ENV", file=f)
    print("ENV PATH=\"$VIRTUAL_ENV/bin:$PATH\"", file=f)

    # Install Dependencies
    print("RUN pip install --no-cache-dir", end=' ', file=f)

    for item in package_list:
        for value in item.values():
            print(value, end=' ', file=f)
    print(file=f)

# Execution of Model Build
    print('COPY ' + executable + ' /app/' + executable, file=f)
    print('CMD "[' + core_name + '", "' + executable + '"]', file=f)

print(f"Output successfully written to {OUTPUT_FILE}")
