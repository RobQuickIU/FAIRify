# Return card contents to the terminal. Formatted for human consumption.
# Return card contents to the terminal. Formatted for human consumption.
import sys
import os
import yaml

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add it to Python path so we can import get.py
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import get_yaml_cards function from get.py
from get import get_yaml_cards

def view_card(card_name):
    """Display a specific card's contents in a human-readable format."""
    import sys
    
    # Get all cards from server
    print(f"Fetching cards from server...", flush=True)
    yaml_dict = get_yaml_cards()
    
    if not yaml_dict:
        print("❌ No cards retrieved from server.", flush=True)
        return None
    
    # Check if card exists
    if card_name not in yaml_dict:
        print(f"❌ Card '{card_name}' not found.", flush=True)
        print(f"\nAvailable cards ({len(yaml_dict)}):", flush=True)
        for name in sorted(yaml_dict.keys()):
            print(f"  - {name}", flush=True)
        sys.stdout.flush()
        return None
    
    # Get the card data
    card_data = yaml_dict[card_name]
    
    # Display the card
    print(f"\n{'='*60}", flush=True)
    print(f"Card: {card_name}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    # Format as YAML for readability
    formatted_yaml = yaml.dump(card_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(formatted_yaml, flush=True)
    sys.stdout.flush()
    
    return card_data

def view_all_cards():
    """Display all cards in a formatted way."""
    yaml_dict = get_yaml_cards()
    
    if not yaml_dict:
        print("No cards found.")
        return
    
    print(f"\n{'='*60}")
    print(f"All Cards ({len(yaml_dict)} total)")
    print(f"{'='*60}\n")
    
    for i, (card_name, card_data) in enumerate(sorted(yaml_dict.items()), 1):
        print(f"\n{'-'*60}")
        print(f"{i}. {card_name}")
        print(f"{'-'*60}")
        formatted_yaml = yaml.dump(card_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(formatted_yaml)

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            view_all_cards()
        else:
            # Get the card name (might be with or without .yaml extension)
            card_name = sys.argv[1]
            # Try with .yaml extension if not present
            yaml_dict = get_yaml_cards()
            if card_name not in yaml_dict and not card_name.endswith('.yaml'):
                card_name_with_ext = card_name + '.yaml'
                if card_name_with_ext in yaml_dict:
                    card_name = card_name_with_ext
            view_card(card_name)
    else:
        # No arguments, show usage and available cards
        print("Usage:")
        print("  python view.py <card_name>     # View a specific card")
        print("  python view.py --all           # View all cards")
        print("\nFetching available cards...")
        yaml_dict = get_yaml_cards()
        if yaml_dict:
            print(f"\nAvailable cards ({len(yaml_dict)}):")
            for name in sorted(yaml_dict.keys()):
                print(f"  - {name}")
        else:
            print("No cards found.")
