#!/usr/bin/env python3
"""Fetch the current revised legislation of Tonga from the official AGO site (ago.gov.to, WWT4 CMS).

1. POSTs the A..Z selector of 'Current Revised Edition > by Title' and saves the listings.
2. Parses principal Acts and their subordinate legislation (English + Tongan PDF links).
3. Downloads the PDFs (verified complete) into RAW/pdf/.
Usage: to_fetch.py RAW_DIR
"""
import json, os, re, string, sys, time, datetime
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

BASE = "https://ago.gov.to"
LIST = BASE + "/cms/legislation/current-revised-edition/by-title.html?view=acts_alpha"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = sys.argv[1]
S = requests.Session()
S.headers["User-Agent"] = UA


def listing(letter):
    p = os.path.join(RAW, "list", f"{letter}.html")
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()
    pit = datetime.date.today().isoformat() + " 00:00:00"
    for a in range(5):
        try:
            r = S.post(LIST, data={"submit4": letter, "pointintime": pit}, timeout=120)
            if r.status_code == 200:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(r.text)
                return r.text
        except Exception as e:
            print("ERR", letter, e, file=sys.stderr)
        time.sleep(5 * 2 ** a)
    raise RuntimeError(letter)


def tip(td):
    d = td.find(attrs={"data-content": True}) if td else None
    if not d:
        return ""
    return BeautifulSoup(d["data-content"], "lxml").get_text("\n", strip=True)


def parse(html):
    s = BeautifulSoup(html, "lxml")
    tb = s.find("table")
    out, parent = [], None
    if not tb:
        return out
    for tr in tb.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 7:
            continue
        cls = " ".join(tds[3].get("class") or [])
        kind = "amd" if "amd" in cls else "sub" if "sub" in cls else "principal"
        en, to = tds[3].find("a", href=True), tds[4].find("a", href=True)
        note = tip(tds[1])
        m = re.search(r"Item Number\s*:\s*(\S+)", note)
        rec = {
            "kind": kind,
            "item": m.group(1) if m else None,
            "note": re.sub(r"^Item Number\s*:\s*\S+\s*", "", note).strip(),
            "title_en": re.sub(r"^amended by\.\.\.\s*", "", tds[3].get_text(" ", strip=True)),
            "pdf_en": BASE + en["href"] if en else None,
            "title_to": re.sub(r"^amended by\.\.\.\s*", "", tds[4].get_text(" ", strip=True)),
            "pdf_to": BASE + to["href"] if to else None,
            "subject": re.sub(r"^Subject\s*:\s*", "", tip(tds[5])).strip(),
            "commenced": re.sub(r"^Date Commenced\s*:\s*", "", tip(tds[6])).strip().split("\n")[0],
        }
        if kind == "principal":
            parent = rec
        else:
            rec["parent_item"] = parent["item"] if parent else None
            rec["parent_title"] = parent["title_en"] if parent else None
        out.append(rec)
    return out


def dl(url):
    if not url:
        return None
    rel = url.split("/cms/images/LEGISLATION/", 1)[-1]
    p = os.path.join(RAW, "pdf", rel)
    if os.path.exists(p):
        return p
    os.makedirs(os.path.dirname(p), exist_ok=True)
    for a in range(5):
        try:
            r = S.get(url, timeout=300)
            if r.status_code == 200 and r.content[:5] == b"%PDF-" and b"%%EOF" in r.content[-1024:]:
                with open(p + ".tmp", "wb") as f:
                    f.write(r.content)
                os.replace(p + ".tmp", p)
                return p
            print("bad", r.status_code, len(r.content), url, file=sys.stderr)
            if r.status_code == 404:
                return None
        except Exception as e:
            print("ERR", url, e, file=sys.stderr)
        time.sleep(3 * 2 ** a)
    return None


def main():
    os.makedirs(os.path.join(RAW, "list"), exist_ok=True)
    recs = []
    for L in string.ascii_uppercase:
        recs += parse(listing(L))
    keep = [r for r in recs if r["kind"] in ("principal", "sub")]
    print(len(recs), "rows;", sum(r["kind"] == "principal" for r in recs), "principal;",
          sum(r["kind"] == "sub" for r in recs), "subordinate")
    urls = [u for r in keep for u in (r["pdf_en"], r["pdf_to"]) if u]
    with ThreadPoolExecutor(2) as ex:
        res = dict(zip(urls, ex.map(dl, urls)))
    for r in keep:
        r["file_en"] = res.get(r["pdf_en"])
        r["file_to"] = res.get(r["pdf_to"])
    with open(os.path.join(RAW, "index.json"), "w") as f:
        json.dump(keep, f, indent=1, ensure_ascii=False)
    print("missing:", sum(1 for u in urls if not res.get(u)))


if __name__ == "__main__":
    main()
