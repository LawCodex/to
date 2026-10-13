#!/usr/bin/env python3
"""Convert the Tonga PDFs fetched by to_fetch.py into LawCodex Markdown.

Usage: to_convert.py RAW_DIR OUT_DIR
Layout: <lang>/constitution/, <lang>/acts/, <lang>/subordinate/<parent-act>/  (lang = en | to)
"""
import datetime, json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import to_pdf2md  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
TODAY = datetime.date.today().isoformat()


def slug(s, n=80):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-")


def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def clean_title(t):
    t = re.sub(r"\s*\[\d+\]\s*$", "", t or "").strip()
    t = re.sub(r"\.pdf\b", "", t)
    return re.sub(r"\s+", " ", t)


def version(t):
    m = re.search(r"\[(\d+)\]\s*$", t or "")
    return m.group(1) if m else None


def parse_date(s):
    try:
        return datetime.datetime.strptime(s.strip(), "%A, %d %B %Y").date().isoformat()
    except Exception:
        return None


def main():
    recs = json.load(open(os.path.join(RAW, "index.json")))
    counts = {}
    report = []
    parent_slug = {}
    for r in recs:
        if r["kind"] == "principal":
            parent_slug[r["item"]] = f"{r['item']}-{slug(clean_title(r['title_en']))}"
    for r in recs:
        for lang in ("en", "to"):
            f = r.get(f"file_{lang}")
            if not f or not os.path.exists(f):
                if r.get(f"pdf_{lang}"):
                    report.append(("missing", lang, r[f"pdf_{lang}"]))
                continue
            try:
                body, info = to_pdf2md.convert(f)
            except Exception as e:
                report.append(("error", lang, r[f"pdf_{lang}"], str(e)))
                continue
            if len(body.strip()) < 200:
                report.append(("empty", lang, r[f"pdf_{lang}"]))
                continue
            title = clean_title(r[f"title_{lang}"]) or clean_title(r["title_en"])
            en_title = clean_title(r["title_en"])
            is_const = r["kind"] == "principal" and en_title.lower() == "constitution of tonga"
            kind = "constitution" if is_const else ("act" if r["kind"] == "principal" else "subordinate")
            base = f"{r['item']}-{slug(en_title)}"
            if is_const:
                rel = os.path.join(lang, "constitution", base + ".md")
            elif r["kind"] == "principal":
                rel = os.path.join(lang, "acts", base + ".md")
            else:
                rel = os.path.join(lang, "subordinate", parent_slug.get(r.get("parent_item"), "other"), base + ".md")
            fm = ["---", f"title: {yq(title)}"]
            if lang != "en":
                fm.append(f"title_en: {yq(en_title)}")
            fm += [f"identifier: {yq(r['item'])}", f"type: {kind}", "jurisdiction: to", f"language: {lang}"]
            m = re.match(r"(\d{4})-", r["item"] or "")
            if m:
                fm.append(f"year: {m.group(1)}")
            d = parse_date(r.get("commenced") or "")
            if d:
                fm.append(f"version_commenced: {d}")
            v = version(r[f"title_{lang}"])
            if v:
                fm.append(f"version: {v}")
            if r.get("subject"):
                fm.append(f"subject: {yq(r['subject'])}")
            if r["kind"] != "principal" and r.get("parent_title"):
                fm.append(f"parent_act: {yq(clean_title(r['parent_title']))}")
            fm += ["status: in_force", f"source: {yq(r[f'pdf_{lang}'])}",
                   'format_note: "text extracted from the official revised-edition PDF; layout not preserved"',
                   f"retrieved: {TODAY}", "---", ""]
            head = f"# {title}\n\n"
            p = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(fm) + head + body)
            key = os.path.dirname(rel).split(os.sep)[:2]
            counts["/".join(key)] = counts.get("/".join(key), 0) + 1
    for k in sorted(counts):
        print(k, counts[k])
    with open(os.path.join(RAW, "convert_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print(len(report), "problems (see convert_report.json)")


if __name__ == "__main__":
    main()
