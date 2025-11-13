# Retrieves yaml card from the file server and stores it in an object.

import os
import requests
import yaml

BASE_URL = "https://github.com/RobQuickIU/FAIRify/tree/main/cards/FAIR_cards"
GITHUB_API_URL = (
    "https://api.github.com/repos/RobQuickIU/FAIRify/contents/cards/FAIR_cards?ref=main"
)


def _normalize_yaml_text(raw_text: str) -> str:
    """Clean up the raw text so YAML parsing is less brittle."""
    if raw_text.startswith("\ufeff"):
        raw_text = raw_text[1:]

    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = normalized.split("\n")
    if lines and lines[0].strip().lower() == "metadata":
        idx = 1
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
        lines = lines[idx:]

    processed = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        next_line = lines[idx + 1] if idx + 1 < len(lines) else ""

        # Auto-add missing ":" for keys that precede indented blocks/lists.
        if (
            stripped
            and not stripped.startswith(("#", "-"))
            and ":" not in stripped
            and next_line.startswith((" ", "\t"))
        ):
            processed.append(f"{line}:")
            continue

        # Convert list scalars with nested metadata into dictionaries or quoted scalars.
        if stripped.startswith("-") and ":" not in stripped:
            indent = line[: line.find("-")]
            content = stripped[1:].strip()
            nested_indent = indent + "  "
            if content and next_line.startswith(nested_indent) and ":" in next_line:
                processed.append(f"{indent}- package: {content}")
                j = idx + 1
                while j < len(lines) and lines[j].startswith(nested_indent):
                    nested_line = lines[j].strip()
                    if ":" not in nested_line:
                        parts = nested_line.split(None, 1)
                        if len(parts) == 2:
                            nested_line = f"{parts[0]}: {parts[1]}"
                    processed.append(
                        lines[j][: len(lines[j]) - len(lines[j].lstrip())] + nested_line
                    )
                    j += 1
                continue
            else:
                processed.append(f"{indent}- {content!r}")
                continue

        # Fix isolated package_version entries so they become valid mappings.
        if stripped.startswith("- package_version:"):
            indent = line[: line.find("-")]
            processed.append(f"{indent}package_version:{line.split(':', 1)[1]}")
            continue

        processed.append(line)

    return "\n".join(processed)


def get_yaml_cards():
    """Fetch YAML files from GitHub, parse them, and return as {filename: data}."""
    yaml_dict = {}

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "fairify-card-fetcher",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        entries = response.json()

        if not isinstance(entries, list):
            print(f" Unexpected GitHub response: {entries}")
            return yaml_dict

        yaml_entries = [
            item
            for item in entries
            if item.get("type") == "file" and item.get("name", "").lower().endswith(".yaml")
        ]

        if not yaml_entries:
            print("No YAML files found in GitHub directory listing.")
            return yaml_dict

        for item in yaml_entries:
            filename = item["name"]
            download_url = item.get("download_url")

            if not download_url:
                print(f"  Skipping {filename}; no download URL provided.")
                continue

            try:
                file_response = requests.get(download_url, timeout=30)
                file_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f" Failed to fetch {filename}: {e}")
                continue

            try:
                yaml_text = _normalize_yaml_text(file_response.text)
                parsed_yaml = yaml.safe_load(yaml_text)
                if parsed_yaml is not None:
                    yaml_dict[filename] = parsed_yaml
                    print(f" Successfully loaded: {filename}")
                else:
                    print(f"  Warning: {filename} is empty or None")
            except yaml.YAMLError as e:
                print(f" YAML parsing error for {filename}: {e}")
                snippet = file_response.text.strip().split("\n")[:5]
                print("   First 5 lines:")
                for i, line in enumerate(snippet, 1):
                    print(f"   {i}: {repr(line[:80])}")

    except requests.exceptions.RequestException as e:
        print(f" Failed to fetch GitHub directory listing: {e}")
    except Exception as e:
        print(f" Unexpected error: {e}")

    return yaml_dict


if __name__ == "__main__":
    cards = get_yaml_cards()
    print(f"\n Summary: Retrieved {len(cards)} YAML cards")
    if cards:
        print("Available cards:")
        for filename in cards.keys():
            print(f"  - {filename}")
