# Builds a model based on the algorithm and the specified model.

# Ask user if they would like to build a ViT, DistilBERT, or Whisper model.

# Step 2. Pull the container from http://149.165.155.66/fair-containers/containers/ model building has _build.tar in containers.

# Step 3. Excute the build. docker 'run whisper_build'

# build_model.py
import requests
import subprocess
from pathlib import Path

BASE_URL = "http://149.165.155.66/fair-containers/containers"

MODELS = {
    "1": {"name": "DistilBERT", "tar": "distilbert_build.tar", "image": "distilbert_build:0.1"},
    "2": {"name": "ViT",        "tar": "vit_build.tar",        "image": "vit_build:0.1"},
    "3": {"name": "Whisper",    "tar": "whisper_build.tar",    "image": "whisper_build:0.1"},
}


DOWNLOAD_DIR = Path("/home/exouser/containers")  # absolute path so we know where it goes
DOWNLOAD_DIR.mkdir(exist_ok=True)

def main():
    print("Which model do you want to build?")
    print("  1) DistilBERT")
    print("  2) ViT")
    print("  3) Whisper")
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice not in MODELS:
        print("Invalid choice.")
        return

    cfg = MODELS[choice]
    url = f"{BASE_URL}/{cfg['tar']}"
    tar_path = DOWNLOAD_DIR / cfg["tar"]

    print(f"\nSelected: {cfg['name']}")
    print(f"URL:      {url}")
    print(f"Saving to:{tar_path}")

    # Download
    print("\nDownloading...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    size = 0
    with tar_path.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                size += len(chunk)
                print(f"\r  Downloaded: {size / (1024**2):.1f} MB", end="")
    print("\nDownload done.")

    # docker load
    print("\nLoading into Docker...")
    subprocess.run(["docker", "load", "-i", str(tar_path)], check=True)
    print("docker load done.")

    # docker run
    print(f"\nRunning: docker run {cfg['image']}")
    subprocess.run(["docker", "run", cfg["image"]], check=True)
    print("Container finished.")

if __name__ == "__main__":
    main()
