from nltk.corpus import stopwords
from rake_nltk import Rake
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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


def filter_external_links(urls, exclusion_list, inclusion_list):
    """
    Filters URLs based on exclusion and inclusion lists.

    Args:
        urls (list): List of scraped URLs.
        exclusion_list (list): URLs to exclude.
        inclusion_list (list): URLs to always include.

    Returns:
        dict: Filtered results including 'excluded', 'included', and 'filtered' URLs.
    """
    excluded = []
    included = []
    filtered = []

    for url in urls:
        if url in exclusion_list:
            excluded.append(url)
        elif url in inclusion_list:
            included.append(url)
        else:
            filtered.append(url)

    return {"excluded": excluded, "included": included, "filtered": filtered}


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
    blog_data["processed_keywords"] = blog_data["keywords"].apply(preprocess_text)
    blog_data["processed_title"] = blog_data["title"].apply(preprocess_text)
    combined_data = blog_data["processed_keywords"] + " " + blog_data["processed_title"] * title_weight
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.8)
    vectors = vectorizer.fit_transform(combined_data.tolist() + [content_cleaned])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    blog_data["relevance"] = similarities
    suggestions = blog_data[blog_data["relevance"] >= threshold].nlargest(10, "relevance")
    suggestions["relevance (%)"] = (suggestions["relevance"] * 100).round(2)
    return suggestions[["title", "url", "relevance (%)"]]
