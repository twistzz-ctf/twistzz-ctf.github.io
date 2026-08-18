#!/usr/bin/env python3
import re
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import html2text

OLD_SITE = "/home/ala/blogs"
OUT_DIR = "/home/ala/twistzz-blogs/source/_posts"

os.makedirs(OUT_DIR, exist_ok=True)

h = html2text.HTML2Text()
h.body_width = 0
h.unicode_snob = True
h.protect_links = True
h.wrap_links = False
h.single_line_break = False
h.mark_code = False

def slug_from_url(url):
    return url.strip("/").split("/")[-1]

def extract_code_blocks(soup):
    placeholders = {}
    for i, fig in enumerate(soup.find_all("figure", class_="highlight")):
        classes = fig.get("class", [])
        lang = ""
        for c in classes:
            if c != "highlight":
                lang = c
                break
        lines = []
        for span in fig.select("td.code pre > span.line"):
            lines.append(span.get_text())
        code_text = "\n".join(lines)
        token = f"@@CODEBLOCK_{i}@@"
        placeholders[token] = (lang, code_text)
        fig.replace_with(token)
    return placeholders

def convert_content(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    # strip empty headerlink anchors, keep heading text
    for a in soup.select("a.headerlink"):
        a.decompose()
    placeholders = extract_code_blocks(soup)
    raw_html = str(soup)
    md = h.handle(raw_html)
    for token, (lang, code) in placeholders.items():
        fenced = f"\n```{lang}\n{code}\n```\n"
        md = md.replace(token, fenced)
    # strip trailing whitespace per line, collapse 3+ blank lines
    md = "\n".join(line.rstrip() for line in md.split("\n"))
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"

def get_post_meta(url):
    path = os.path.join(OLD_SITE, url.strip("/"), "index.html")
    with open(path, encoding="utf-8") as f:
        page = f.read()
    soup = BeautifulSoup(page, "lxml")

    date = None
    time_tag = soup.select_one("#post-meta time[datetime]")
    if time_tag:
        title_attr = time_tag.get("title", "")
        m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", title_attr)
        if m:
            date = m.group(1)
        else:
            date = time_tag["datetime"].replace("T", " ").replace(".000Z", "")

    categories = [a.get_text(strip=True) for a in soup.select("span.post-meta-categories a.post-meta-categories")]
    tags = [a.get_text(strip=True) for a in soup.select("div.post-meta__tag-list a.post-meta__tags")]

    return date, categories, tags

def yaml_escape(s):
    if any(c in s for c in ':#[]{}&*!|>\'"%@`') or s.strip() != s:
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s

def build_front_matter(title, date, categories, tags):
    lines = ["---"]
    lines.append(f"title: {yaml_escape(title)}")
    if date:
        lines.append(f"date: {date}")
    if categories:
        lines.append("categories:")
        for c in categories:
            lines.append(f"  - {yaml_escape(c)}")
    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f"  - {yaml_escape(t)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"

def main():
    tree = ET.parse(os.path.join(OLD_SITE, "search.xml"))
    root = tree.getroot()
    entries = root.findall("entry")
    print(f"total entries: {len(entries)}")
    count = 0
    for e in entries:
        title = e.find("title").text or "Untitled"
        url = e.find("url").text
        content_html = e.find("content").text or ""

        date, categories, tags = get_post_meta(url)
        md_body = convert_content(content_html)
        front_matter = build_front_matter(title, date, categories, tags)

        slug = slug_from_url(url)
        out_path = os.path.join(OUT_DIR, f"{slug}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(front_matter + md_body)
        count += 1
    print(f"wrote {count} posts to {OUT_DIR}")

if __name__ == "__main__":
    main()
