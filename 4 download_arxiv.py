import requests
import re
from arxiv import arxiv_to_json

def download_arxiv(url):
    response = requests.get(url)

    pattern = re.compile(
        r'(<div class="leftcolumn">.*?<div style="clear:both;"></div>)',
        re.DOTALL
    )

    match = pattern.search(response.text)
    if match:
        extracted = match.group(1)
    
    return arxiv_to_json(extracted)

if __name__ == "__main__":

    import pandas as pd

    df = pd.read_csv("papers_clean.tsv", sep="\t", encoding="utf-8")
    # df = df[df["Paper-Link"].str.contains("arxiv.org/abs/")]
    
    url = "https://arxiv.org/abs/2506.17298"
    data = download_arxiv(url)

    print(data)