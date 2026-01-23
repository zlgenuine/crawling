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


def search_pdf(title, retry=5):
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
                pdfs = [r.get("url","") for r in results if r.get("url","").lower().endswith(".pdf")]
                return pdfs
            except Exception as e:
                print("json解析失败：",e)
                return []
        else:
            print(f"第 {i+1} 次请求失败，状态码：{response.status_code}")
            time.sleep(2)  # 等待 2 秒再重试
        
    return []

def search_serpapi(title,serpapi_key="e3e5bdf3db175a00f6fdd33fabaacd1032b9680f7c07e1e4db25540f13f7628e",num=10):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": title,
        "num": num,
        "api_key": serpapi_key
    }

    res = requests.get(url, params=params)
    data = res.json() 
    
    pdf_links = []
    for item in data.get("organic_results", []):
        link = item.get("link", "")
        if link.lower().endswith(".pdf"):
            pdf_links.append(link)

    return pdf_links
    


if __name__ == "__main__":
    titles_pth = "concensus.csv"
    download_links = []
    df = pd.read_csv(titles_pth)
    titles = df["Title"]
    for idx, title in enumerate(titles):
        pdfs = search_pdf(title)
        if pdfs:
            print(f"No. {idx}: {pdfs}")
            pdfs = [";".join(x) for x in pdfs]
            download_links.append(pdfs)
        else:
            pdfs = search_serpapi(title)
            if pdfs:
                print(f"No. {idx}: {pdfs}")
                pdfs = [";".join(x) for x in pdfs]
                download_links.append(pdfs)
            else:
                print(f"No. {idx}: No pdf found")
                download_links.append(['none'])
    pdf_df = pd.DataFrame({"links": download_links})
    pdf_df.to_csv("links.csv", index=False, encoding="utf-8-sig")
    