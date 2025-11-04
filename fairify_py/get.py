# Retrieves yaml card from the file server and stores it in an object.

import requests
import re
import yaml

BASE_URL = "http://149.165.155.66/fairify/"

def get_yaml_cards():
    """Fetch YAML files from the server, parse them, and return as a dictionary."""
    yaml_dict = {}
    
    try:
        # Get directory listing
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()
        html = response.text
        
        # Extract YAML file links
        yaml_links = re.findall(r'href="([^"]+\.yaml)"', html)
        
        if not yaml_links:
            print("No YAML files found in directory listing.")
            return yaml_dict
        
        # Fetch and parse each YAML file
        for link in yaml_links:
            file_url = BASE_URL + link
            filename = link.split('/')[-1]  # Get just the filename
            
            try:
                # Fetch the YAML file
                file_response = requests.get(file_url, timeout=30)
                file_response.raise_for_status()
                
                # Clean and parse the YAML content
                try:
                    # Get text with proper encoding
                    yaml_text = file_response.text
                    
                    # Remove BOM if present
                    if yaml_text.startswith('\ufeff'):
                        yaml_text = yaml_text[1:]
                    
                    # Strip leading/trailing whitespace and normalize line endings
                    yaml_text = yaml_text.strip().replace('\r\n', '\n').replace('\r', '\n')
                    
                    # Remove "metadata" prefix if present (some files start with "metadata\n\n")
                    lines = yaml_text.split('\n')
                    if lines and lines[0].strip() == 'metadata':
                        # Skip the "metadata" line and any following empty lines
                        start_idx = 1
                        while start_idx < len(lines) and not lines[start_idx].strip():
                            start_idx += 1
                        yaml_text = '\n'.join(lines[start_idx:])
                    
                    # Try to parse the YAML
                    parsed_yaml = yaml.safe_load(yaml_text)
                    if parsed_yaml is not None:
                        yaml_dict[filename] = parsed_yaml
                        print(f"✅ Successfully loaded: {filename}")
                    else:
                        print(f"⚠️  Warning: {filename} is empty or None")
                except yaml.YAMLError as e:
                    print(f"❌ YAML parsing error for {filename}: {e}")
                    # Show first few lines for debugging
                    lines = file_response.text.strip().split('\n')[:5]
                    print(f"   First 5 lines:")
                    for i, line in enumerate(lines, 1):
                        print(f"   {i}: {repr(line[:80])}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to fetch {filename}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error with {filename}: {e}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch directory listing: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return yaml_dict

if __name__ == "__main__":
    cards = get_yaml_cards()
    print(f"\n📊 Summary: Retrieved {len(cards)} YAML cards")
    if cards:
        print("Available cards:")
        for filename in cards.keys():
            print(f"  - {filename}")
