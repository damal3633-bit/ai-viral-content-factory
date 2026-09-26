import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

RSS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"


def get_trends(limit=5):
    request = Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(RSS_URL, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")

    trends = []
    seen = set()

    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()

        if not title:
            continue

        if title.lower() in seen:
            continue

        seen.add(title.lower())

        trends.append({
            "title": title,
            "url": link
        })

        if len(trends) >= limit:
            break

    return trends
