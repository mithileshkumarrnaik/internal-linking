import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def fetch_sitemap_urls(sitemaps):
    urls = []
    for sitemap in sitemaps:
        try:
            root = ET.fromstring(requests.get(sitemap).content)
            urls.extend(url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"))
        except Exception as e:
            print(f"Error with sitemap {sitemap}: {e}")
    return urls

def scrape_blog_data(urls, word_limit=1000):
    def fetch_blog_data(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else "Title not found"
            content = soup.find('div', class_='main-content') or soup.find('article') or soup.find('section')
            text = content.get_text(" ").strip() if content else "Content not found"
            return {"url": url, "title": title, "content": " ".join(text.split()[:word_limit])}
        except Exception as e:
            return {"url": url, "title": "Error", "content": f"Error: {e}"}
    return [fetch_blog_data(url) for url in urls]
