import os
import time
import requests
from Bio import Entrez
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from openai import OpenAI
from datasets import load_dataset
from tqdm import tqdm
import csv
from pathlib import Path


def search_pdf(title, retry=30):
    url = "http://104.194.90.24:18081/tavilysearch"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-7izCWzKkQXDWuxU9FYP85mIg8SNSfUOn93MBEQtqdTr37K7T"
    }
    data = {"query": title + " pdf"}
    
    for i in range(retry):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                results = response.json().get("results", [])

                # 筛选出 PDF 且有 score
                pdfs = [
                    r for r in results
                    if r.get("url", "").lower().endswith(".pdf") 
                    and r.get("score") is not None
                ]

                # 没有 PDF 时返回 None
                if not pdfs:
                    return None

                # 取 score 最大的
                best_url = max(pdfs, key=lambda x: x["score"])["url"]
                return best_url

            except Exception as e:
                print("json解析失败：", e)
                return None
        else:
            print(f"第 {i+1} 次请求失败，状态码：{response.status_code}")
            time.sleep(2)

    return None

def search_serpapi(title, serpapi_key="e3e5bdf3db175a00f6fdd33fabaacd1032b9680f7c07e1e4db25540f13f7628e", num=30):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": title,
        "num": num,
        "api_key": serpapi_key
    }

    res = requests.get(url, params=params)
    data = res.json()

    best_pdf = None
    best_position = float("inf")

    for item in data.get("organic_results", []):
        link = item.get("link", "")
        position = item.get("position", None)

        # 只要 PDF
        if link.lower().endswith(".pdf"):

            # position 存在才判断
            if position is not None and position < best_position:
                best_position = position
                best_pdf = link

    return best_pdf

    
def download_first_available(url, output_path, timeout=30):
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




if __name__ == "__main__":
    titles_pth = "concensus.csv"
    download_links = []
    df = pd.read_csv(titles_pth)
    titles = df["Title"]
    
    fieldnames = ["id", "title", "link"]
    with open("links_downloaded.csv","a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, title in enumerate(titles):
            if idx > -1:
                pdfs = search_pdf(title)
                if pdfs:
                    print(f"No. {idx}: {pdfs}")
                    download_first_available(
                        url=pdfs,
                        output_path=Path(r"C:\Users\Administrator\Desktop\crawling\crawling\concensus_pdfs") / f"{sanitize_filename(title)}.pdf"
                        )
                    writer.writerow({
                        "id": idx,
                        "title": title,
                        "link":pdfs
                    })
                else:
                    pdfs = search_serpapi(title)
                    if pdfs:
                        print(f"No. {idx}: {pdfs}")
                        download_first_available(
                        url=pdfs,
                        output_path=Path(r"C:\Users\Administrator\Desktop\crawling\crawling\concensus_pdfs") / f"{sanitize_filename(title)}.pdf"
                        )
                        writer.writerow({
                        "id": idx,
                        "title": title,
                        "link":pdfs
                    })
                    else:
                        print(f"No. {idx}: No pdf found")
                        writer.writerow({
                        "id": idx,
                        "title": title,
                        "link":pdfs
                    })
