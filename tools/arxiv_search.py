"""Query the arXiv API (primary source) and print title, id, date, authors and abstract.

Usage:
  python tools/arxiv_search.py 'search_query=abs:watermark AND abs:steering&sortBy=submittedDate&sortOrder=descending&max_results=10' [abstract_chars]
  python tools/arxiv_search.py 'id_list=2606.06315,2605.05443' 
Notes: use https (plain http returns an empty body); spaces and quotes are URL-encoded here.
"""
import sys
import urllib.request
import xml.etree.ElementTree as E

NS = {"a": "http://www.w3.org/2005/Atom"}


def query(q):
    q = q.replace(" ", "%20").replace('"', "%22")
    return urllib.request.urlopen("https://export.arxiv.org/api/query?" + q, timeout=60).read()


def main():
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    for e in E.fromstring(query(sys.argv[1])).findall("a:entry", NS):
        title = " ".join(e.find("a:title", NS).text.split())
        arxiv_id = e.find("a:id", NS).text.split("/abs/")[-1]
        date = e.find("a:published", NS).text[:10]
        authors = [a.find("a:name", NS).text for a in e.findall("a:author", NS)]
        summary = " ".join(e.find("a:summary", NS).text.split())
        more = " et al." if len(authors) > 4 else ""
        print(f"## {title}\n{arxiv_id} | {date} | {', '.join(authors[:4])}{more}\n{summary[:n]}\n")


if __name__ == "__main__":
    main()
