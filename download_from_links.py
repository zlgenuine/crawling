import requests
from pathlib import Path

def download_first_available(urls, output_path, timeout=15):
    output_path = Path(output_path)

    for url in urls:
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                if "application/pdf" not in r.headers.get("Content-Type", "").lower():
                    continue

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


download_links = [
    "https://www.mdpi.com/2077-0383/15/2/528/pdf",
    "https://example.com/backup.pdf"
]

download_first_available(
    urls=download_links,
    output_path="Saudi_Low_Back_Pain_Guideline_2022.pdf"
)
