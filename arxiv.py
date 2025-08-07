import json
from bs4 import BeautifulSoup

# with open("arxiv_page.html", encoding="utf-8") as f:
#     soup = BeautifulSoup(f, "html.parser")

def arxiv_to_json(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    def get_text(selector, parent=soup, strip=True):
        el = parent.select_one(selector)
        return el.get_text(strip=strip)[6:] if el else None

    def get_authors():
        authors_div = soup.select_one("div.authors")
        if not authors_div:
            return []
        return [a.get_text(strip=True) for a in authors_div.find_all("a")]

    def get_links():
        links = {}
        pdf = soup.find("a", string=lambda s: s and "PDF" in s)
        html = soup.find("a", string=lambda s: s and "HTML" in s)
        tex = soup.find("a", string=lambda s: s and "TeX Source" in s)
        doi = soup.find("a", id="arxiv-doi-link")
        links["pdf"] = pdf["href"] if pdf else None
        links["html"] = html["href"] if html else None
        links["tex"] = tex["href"] if tex else None
        links["doi"] = doi["href"] if doi else None
        return links

    def get_subjects():
        subj_td = soup.find("td", class_="tablecell subjects")
        if not subj_td:
            return []
        # Split on semicolon, strip whitespace and commas
        return [
            s.strip(" ,").strip()
            for s in subj_td.get_text().split(";")
            if s.strip(" ,")
        ]

    def get_submission_history():
        div = soup.find("div", class_="submission-history")
        if not div:
            return None
        return div.get_text(" ", strip=True)

    def get_references():
        refs_section = soup.find("h3", string=lambda s: s and "References" in s)
        if not refs_section:
            return []
        ul = refs_section.find_next("ul")
        if not ul:
            return []
        refs = []
        for li in ul.find_all("li"):
            a = li.find("a")
            refs.append({
                "label": a.get_text(strip=True) if a else li.get_text(strip=True),
                "url": a["href"] if a and a.has_attr("href") else None
            })
        return refs

    def get_category():
        h1 = soup.select_one("div.subheader > h1")
        return h1.get_text(strip=True) if h1 else None

    data = {
        "arxiv_id": get_text(".header-breadcrumbs-mobile strong"),
        "category": get_category(),
        "title": get_text("h1.title"),
        "authors": get_authors(),
        "abstract": get_text("blockquote.abstract"),
        "comments": get_text("td.comments"),
        "subjects": get_subjects(),
        "links": get_links(),
        "submission_history": get_submission_history(),
        "references_and_citations": get_references(),
    }

    return data

# print(json.dumps(data, indent=2, ensure_ascii=False))