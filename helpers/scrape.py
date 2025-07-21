import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import sqlite3
import os

def init_db():
    conn = sqlite3.connect('scraped_blogs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS blogs
                 (url TEXT PRIMARY KEY, title TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def save_blog_to_db(url, title, content):
    conn = sqlite3.connect('scraped_blogs.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO blogs VALUES (?, ?, ?)', (url, title, content))
    conn.commit()
    conn.close()

def load_blogs_from_db():
    conn = sqlite3.connect('scraped_blogs.db')
    c = conn.cursor()
    c.execute('SELECT url, title, content FROM blogs')
    rows = c.fetchall()
    conn.close()
    return [{'url': url, 'title': title, 'content': content} for url, title, content in rows]

def fetch_sitemap_urls(sitemaps):
    """
    Fetches and extracts URLs from a list of sitemap URLs.
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
    Scrapes blog content from a list of URLs, using the database to avoid re-scraping.
    """
    init_db()
    # Load already-scraped blogs from DB
    db_blogs = {blog['url']: blog for blog in load_blogs_from_db()}
    results = []
    for url in urls:
        if url in db_blogs:
            results.append(db_blogs[url])
            continue
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else "No Title"
            content = soup.find('div', class_='main-content') or soup.find('article') or soup.find('section')
            text = content.get_text(" ").strip() if content else "No Content"
            text = " ".join(text.split()[:word_limit])
            save_blog_to_db(url, title, text)
            results.append({'url': url, 'title': title, 'content': text})
        except Exception as e:
            results.append({'url': url, 'title': 'Error', 'content': f'Error fetching content: {e}'})
    return results
