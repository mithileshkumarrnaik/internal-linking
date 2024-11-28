# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import csv

# Fetch and extract URLs from sitemaps
def fetch_sitemap_urls(sitemaps):
    urls = []
    for sitemap in sitemaps:
        try:
            root = ET.fromstring(requests.get(sitemap).content)
            urls.extend(url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"))
        except Exception as e:
            print(f"Error with sitemap {sitemap}: {e}")
    return urls

# Save URLs to CSV
def save_urls_to_csv(filename, urls):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerows([['url']] + [[url] for url in urls])

# Input and execution
sitemaps = ["https://acviss.com/page-sitemap.xml", "https://blog.acviss.com/sitemap-post.xml"]
all_urls = fetch_sitemap_urls(sitemaps)
save_urls_to_csv("url.csv", all_urls)
print(f"Total pages extracted: {len(all_urls)}")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

# Fetch blog data
def fetch_blog_data(url, word_limit=1000):
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

# Scrape URLs from CSV
def scrape_urls(file_path, word_limit=1000):
    try:
        urls = pd.read_csv(file_path)['url']
        return pd.DataFrame([fetch_blog_data(url, word_limit) for url in tqdm(urls, desc="Scraping URLs")])
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Main
if __name__ == "__main__":
    input_csv = '/content/url.csv'
    output_csv = '/content/scraped_urls.csv'
    word_limit = int(input("Enter max words to extract (default 1000): ") or 1000)

    print("Scraping started...")
    data = scrape_urls(input_csv, word_limit)
    if not data.empty:
        data.to_csv(output_csv, index=False)
        print(f"Data saved to '{output_csv}'")
    else:
        print("No data scraped. Check the input file or URLs.")

import nltk
nltk.download('punkt_tab') # Download the punkt_tab data
nltk.download('stopwords')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import re
from urllib.parse import urlparse
import pandas as pd
from nltk.corpus import stopwords
from rake_nltk import Rake

# Extract keywords from URL
def extract_keywords_from_url(url):
    try:
        path = urlparse(url).path
        keywords = re.split(r'[-/]', path)
        return [word for word in keywords if word.isalpha() and word.lower() not in stopwords.words('english')]
    except Exception as e:
        return []

# Extract keywords using RAKE
def extract_keywords_with_rake(text, num_keywords=10):
    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        return rake.get_ranked_phrases()[:num_keywords]
    except Exception as e:
        return []

# Generate target keywords
def generate_target_keywords(data, num_keywords=10):
    data['keywords'] = data.apply(
        lambda row: ", ".join(
            set(
                extract_keywords_from_url(row['url']) +
                extract_keywords_with_rake(row['title'], num_keywords) +
                extract_keywords_with_rake(row['content'], num_keywords)
            )
        ),
        axis=1
    )
    return data

# Main workflow
if __name__ == "__main__":
    file_path = '/content/scraped_urls.csv'
    output_path = '/content/target_keywords.csv'

    try:
        print("Loading scraped data...")
        scraped_data = pd.read_csv(file_path)

        print("Generating target keywords...")
        enriched_data = generate_target_keywords(scraped_data)

        enriched_data.to_csv(output_path, index=False)
        print(f"Enriched data saved to '{output_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Load the scraped data
file_path = '/content/scraped_urls.csv'  # Update with the actual file path
data = pd.read_csv(file_path)

# Function to extract keywords from text
def extract_keywords(text, top_n=10):
    if pd.isnull(text):
        return []
    vectorizer = CountVectorizer(stop_words='english', max_features=top_n)
    matrix = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()
    return list(keywords)

# Function to combine and extract target keywords
def generate_target_keywords(row, top_n=10):
    combined_text = f"{row['url']} {row['title']} {row['content']}"
    keywords = extract_keywords(combined_text, top_n)
    return ', '.join(keywords)

# Apply the keyword generation function
data['keywords'] = data.apply(lambda row: generate_target_keywords(row, top_n=20), axis=1)

# Save the updated data to a new CSV
output_file_path = '/content/updated_scraped_urls.csv'  # Update with the desired output path
data.to_csv(output_file_path, index=False)

print(f"Updated data with target keywords saved to {output_file_path}")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from nltk.corpus import stopwords

def preprocess_text(text):
    # Lowercase, remove stopwords and unwanted terms
    stop_words = set(stopwords.words('english')).union({'https', 'com', 'blog', 'www'})
    text = re.sub(r'\W+', ' ', str(text).lower())
    return " ".join(word for word in text.split() if word not in stop_words)

def calculate_relevance(content, blog_data, title_weight=2, threshold=0.15):
    content_cleaned = preprocess_text(content)
    blog_data['processed_keywords'] = blog_data['keywords'].apply(preprocess_text)
    blog_data['processed_title'] = blog_data['title'].apply(preprocess_text)

    combined_data = blog_data['processed_keywords'] + " " + blog_data['processed_title'] * title_weight
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(combined_data.tolist() + [content_cleaned])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    return similarities

def suggest_internal_links(content, blog_data, top_n=30):
    relevance_scores = calculate_relevance(content, blog_data)
    blog_data['relevance'] = relevance_scores
    blog_data = blog_data[blog_data['relevance'] >= 0.15]

    # Sort by relevance score
    suggestions = blog_data.nlargest(top_n, 'relevance')
    suggestions['relevance (%)'] = (suggestions['relevance'] * 100).round(2)

    return suggestions[['title', 'url', 'keywords', 'relevance (%)']]

# Main workflow
def main():
    file_path = '/content/updated_scraped_urls.csv'
    try:
        blog_data = pd.read_csv(file_path)
        blog_data.columns = [col.strip().lower() for col in blog_data.columns]
    except Exception as e:
        print(f"Error: {e}")
        return

    new_blog_content = input("Enter the new blog content: ").strip()
    if not new_blog_content:
        print("Error: Blog content cannot be empty.")
        return

    suggestions = suggest_internal_links(new_blog_content, blog_data)
    if suggestions.empty:
        print("No relevant links found.")
    else:
        print("\nSuggested Internal Links:")
        for idx, row in suggestions.iterrows():
            print(f"{idx + 1}. {row['title']} ({row['relevance (%)']}%)")
            print(f"   URL: {row['url']}")
            print(f"   Matched Keywords: {row['keywords']}\n")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
