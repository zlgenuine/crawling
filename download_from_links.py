import requests
from pathlib import Path
import pandas as pd
import re

def download_first_available(url, output_path, timeout=15):
    if not pd.isna(url):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                print(f"Downloaded successfully from: {url}")
                return True  # stop at first successful download

        except Exception as e:
            print(f"Failed from {url}: {e}")

    print("No download succeeded.")
    return False


def sanitize_filename(name: str, default='file') -> str:
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('._')

    return name if name else default


df = pd.read_csv("links.csv")
rows = list(zip(df["title"],df["link"]))

for idx, row in enumerate(rows):
    download_first_available(
        url=row[1],
        output_path=Path(r"C:\Users\Administrator\Desktop\crawling\crawling\concensus_pdfs") / f"{sanitize_filename(row[0])}.pdf"
    )
