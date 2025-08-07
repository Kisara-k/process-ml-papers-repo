import requests
import re
from arxiv import arxiv_to_json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_arxiv(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        pattern = re.compile(
            r'(<div class="leftcolumn">.*?<div style="clear:both;"></div>)',
            re.DOTALL
        )
        match = pattern.search(response.text)
        if match:
            extracted = match.group(1)
            return arxiv_to_json(extracted)
        else:
            return {"error": "Pattern not found"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    df = pd.read_csv("papers_clean.tsv", sep="\t", encoding="utf-8")
    df = df[df["Paper-Link"].fillna('').str.contains("arxiv.org/abs/")].reset_index(drop=True)
    
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_idx = {
            executor.submit(download_arxiv, row["Paper-Link"]): idx
            for idx, row in df.iterrows()
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            result = future.result()
            results.append((idx, result))

    # Sort results by original index to align with df
    results.sort(key=lambda x: x[0])
    json_dicts = [r[1] for r in results]
    json_df = pd.DataFrame(json_dicts)

    # Concatenate original df (filtered) with the new columns
    final_df = pd.concat([df.reset_index(drop=True), json_df], axis=1)
    final_df = final_df.drop(columns=["has_arxiv"], errors='ignore')

    priority_columns = [
        "Week", "title", "category", "Paper-Link",
    ]
    cols = list(final_df.columns)
    front = [col for col in priority_columns if col in cols]
    rest = [col for col in cols if col not in front]

    final_df = final_df[front + rest]

    final_df.to_csv("arxiv.tsv", sep="\t", index=False, encoding="utf-8")