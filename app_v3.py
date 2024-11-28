import streamlit as st
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from nltk.corpus import stopwords
from rake_nltk import Rake
import nltk
nltk.download('stopwords')

# Helper Functions
def fetch_sitemap_urls(sitemaps):
    urls = []
    for sitemap in sitemaps:
        try:
            root = ET.fromstring(requests.get(sitemap).content)
            urls.extend(url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"))
        except Exception as e:
            st.error(f"Error with sitemap {sitemap}: {e}")
    return urls

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

def preprocess_text(text):
    stop_words = set(stopwords.words('english')).union({'https', 'com', 'blog', 'www'})
    text = re.sub(r'\W+', ' ', str(text).lower())
    return " ".join(word for word in text.split() if word not in stop_words)

def suggest_internal_links(content, blog_data, title_weight=2, threshold=0.15):
    content_cleaned = preprocess_text(content)
    blog_data['processed_keywords'] = blog_data['keywords'].apply(preprocess_text)
    blog_data['processed_title'] = blog_data['title'].apply(preprocess_text)
    combined_data = blog_data['processed_keywords'] + " " + blog_data['processed_title'] * title_weight
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(combined_data.tolist() + [content_cleaned])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    blog_data['relevance'] = similarities
    suggestions = blog_data[blog_data['relevance'] >= threshold].nlargest(10, 'relevance')
    suggestions['relevance (%)'] = (suggestions['relevance'] * 100).round(2)
    return suggestions[['title', 'url', 'relevance (%)']]

# Streamlit Application
st.title("Content Scraper and Link Suggester")

# Sitemap Section
st.header("Step 1: Sitemap Crawling")
sitemaps = st.text_area("Enter sitemap URLs (one per line)", height=100)
if st.button("Fetch URLs"):
    sitemap_list = sitemaps.strip().split("\n")
    urls = fetch_sitemap_urls(sitemap_list)
    if urls:
        st.write(f"Extracted {len(urls)} URLs")
        st.session_state['urls'] = urls
        st.dataframe(urls)
    else:
        st.error("No URLs extracted. Check the sitemap format.")

# Content Scraping Section
st.header("Step 2: Scrape Blog Data")
if "urls" in st.session_state:
    if st.button("Scrape Blogs"):
        scraped_data = [fetch_blog_data(url) for url in st.session_state['urls']]
        scraped_df = pd.DataFrame(scraped_data)
        st.session_state['scraped_data'] = scraped_df
        st.write("Scraped Blog Data")
        st.dataframe(scraped_df)
        scraped_df.to_csv("scraped_data.csv", index=False)
else:
    st.warning("Please fetch URLs first!")

# Keyword Extraction Section
st.header("Step 3: Extract Keywords")
if "scraped_data" in st.session_state:
    if st.button("Generate Keywords"):
        def extract_keywords_with_rake(text, num_keywords=10):
            rake = Rake()
            rake.extract_keywords_from_text(text)
            return ", ".join(rake.get_ranked_phrases()[:num_keywords])
        
        scraped_df = st.session_state['scraped_data']
        scraped_df['keywords'] = scraped_df['content'].apply(lambda x: extract_keywords_with_rake(x))
        st.session_state['scraped_data'] = scraped_df
        st.write("Updated Blog Data with Keywords")
        st.dataframe(scraped_df)
        scraped_df.to_csv("updated_scraped_data.csv", index=False)
else:
    st.warning("Please scrape blogs first!")

# Internal Link Suggestion Section
st.header("Step 4: Suggest Internal Links")
if "scraped_data" in st.session_state:
    blog_content = st.text_area("Enter New Blog Content")
    if st.button("Suggest Links"):
        blog_data = st.session_state['scraped_data']
        suggestions = suggest_internal_links(blog_content, blog_data)
        if not suggestions.empty:
            st.write("Suggested Internal Links")
            st.dataframe(suggestions)
        else:
            st.warning("No relevant links found!")
else:
    st.warning("Please generate keywords first!")
