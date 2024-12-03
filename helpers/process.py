import requests
import xml.etree.ElementTree as ET
import pandas as pd
from nltk.corpus import stopwords
from rake_nltk import Rake
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup


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
    Scrapes blog content from a list of URLs.
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


def load_list(file_path):
    """
    Loads a list of domains/URLs from a text file.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def extract_keywords_with_rake(text, num_keywords=10):
    """
    Extracts keywords from text using RAKE.
    """
    rake = Rake()
    if not text or pd.isna(text):
        return "No content"
    rake.extract_keywords_from_text(str(text))
    return ", ".join(rake.get_ranked_phrases()[:num_keywords])


def filter_external_links(links, exclusion_list, inclusion_list=None):
    """
    Filters links based on exclusion and inclusion lists.
    """
    included = []
    excluded = []
    filtered = []

    for link in links:
        if any(excl in link for excl in exclusion_list):
            excluded.append(link)
        elif inclusion_list and any(incl in link for incl in inclusion_list):
            included.append(link)
        else:
            filtered.append(link)

    return {"included": included, "excluded": excluded, "filtered": filtered}


def preprocess_text(text):
    """
    Preprocesses text by removing stopwords and special characters.
    """
    stop_words = set(stopwords.words('english')).union({'https', 'com', 'blog', 'www'})
    text = re.sub(r'\W+', ' ', str(text).lower())
    return " ".join(word for word in text.split() if word not in stop_words)


def suggest_internal_links(content, blog_data, title_weight=2, threshold=0.15):
    """
    Suggests internal links based on relevance to the given content.
    """
    content_cleaned = preprocess_text(content)
    blog_data["processed_keywords"] 
