import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def fetch_sitemap_urls(sitemaps):
    """
    Fetches and extracts URLs from a list of sitemap URLs.

    Args:
        sitemaps (list): List of sitemap URLs.

    Returns:
        list: List of URLs extracted from the sitemaps.
    """
    urls = []
    for sitemap in sitemaps:
        try:
            response = requests.get(sitemap, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            urls.extend(
                url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            )
        except Exception as e:
            print(f"Error processing sitemap {sitemap}: {e}")
    return urls


def scrape_blog_data(urls, word_limit=1000):
    """
    Scrapes blog content from a list of URLs.

    Args:
        urls (list): List of URLs to scrape.
        word_limit (int): Maximum number of words to extract.

    Returns:
        list: List of dictionaries with scraped content.
    """
    def fetch_blog_content(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else "No Title"
            content = soup.find('div', class_='main-content') or soup.find('article') or soup.find('section')
            text = content.get_text(" ").strip() if content else "No Content"
            return {"url": url, "title": title, "content": " ".join(text.split()[:word_limit])}
        except Exception as e:
            return {"url": url, "title": "Error", "content": f"Error fetching content: {e}"}

    return [fetch_blog_content(url) for url in urls]
