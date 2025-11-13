#placeholder
# Shows the available cards retrieved from the server using get.py
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add it to Python path so we can import get.py
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import get_yaml_cards function from get.py
from get import get_yaml_cards

def list_cards():
    """List all available cards retrieved from the server."""
    # Fetch cards from server using get.py
    yaml_dict = get_yaml_cards()
    # Extract card names (keys) from dictionary
    cards = list(yaml_dict.keys())
    return sorted(cards)

def print_cards():
    """Print all available cards retrieved from the server in a formatted way."""
    cards = list_cards()
    
    if not cards:
        print("No cards found.")
        return
    
    print(f" Available cards from server ({len(cards)}):")
    for i, card in enumerate(cards, 1):
        print(f"  {i}. {card}")

if __name__ == "__main__":
    print_cards()
