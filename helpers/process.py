from nltk.corpus import stopwords
from rake_nltk import Rake
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os


def extract_keywords_with_rake(text, num_keywords=10):
    """
    Extracts keywords from text using RAKE, gracefully handles missing or invalid text.
    """
    rake = Rake()
    try:
        if not text or pd.isna(text):
            return "No content"
        rake.extract_keywords_from_text(str(text))
        return ", ".join(rake.get_ranked_phrases()[:num_keywords])
    except Exception as e:
        return f"Error: {e}"


def filter_pages(scraped_df):
    """
    Filters out pages with titles starting with 'Page ...'.
    """
    return scraped_df[~scraped_df['title'].str.startswith("Page", na=False)]


def preprocess_text(text):
    """
    Preprocesses text by removing stopwords and special characters.
    """
    stop_words = set(stopwords.words('english')).union({'https', 'com', 'blog', 'www'})
    text = re.sub(r'\W+', ' ', str(text).lower())
    return " ".join(word for word in text.split() if word not in stop_words)


def generate_keywords(scraped_df, num_keywords=10):
    """
    Generates keywords for each row in the DataFrame's 'content' column
    using RAKE (Rapid Automatic Keyword Extraction).
    """
    try:
        # Check if 'content' column exists
        if 'content' not in scraped_df.columns:
            raise KeyError("The 'content' column is missing in the DataFrame.")

        # Apply RAKE to extract keywords
        scraped_df['keywords'] = scraped_df['content'].apply(lambda x: extract_keywords_with_rake(x, num_keywords))
        return scraped_df
    except Exception as e:
        raise ValueError(f"Error generating keywords: {e}")


def suggest_internal_links(content, blog_data, title_weight=2, threshold=0.15):
    """
    Suggests internal links based on relevance.
    """
    content_cleaned = preprocess_text(content)
    blog_data['processed_keywords'] = blog_data['keywords'].apply(preprocess_text)
    blog_data['processed_title'] = blog_data['title'].apply(preprocess_text)
    combined_data = blog_data['processed_keywords'] + " " + blog_data['processed_title'] * title_weight
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.8)
    vectors = vectorizer.fit_transform(combined_data.tolist() + [content_cleaned])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    blog_data['relevance'] = similarities
    suggestions = blog_data[blog_data['relevance'] >= threshold].nlargest(50, 'relevance')
    suggestions['relevance (%)'] = (suggestions['relevance'] * 100).round(2)
    return suggestions[['title', 'url', 'relevance (%)']]


def load_list(file_path):
    """
    Loads a list of domains or URLs from a text file.
    Ignores empty lines and comments (#).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Remove empty lines and comments
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def filter_external_links(links, exclusion_list, inclusion_list=None):
    """
    Filters links based on exclusion and inclusion lists.

    Args:
    - links (list): List of links to filter.
    - exclusion_list (list): List of domains/URLs to exclude.
    - inclusion_list (list): List of domains/URLs to prioritize (optional).

    Returns:
    - dict: {'included': [prioritized links], 'filtered': [remaining links]}
    """
    included = []
    filtered = []

    for link in links:
        domain = link.split("/")[2] if "://" in link else link  # Extract domain

        if any(excl in domain for excl in exclusion_list):
            continue  # Skip excluded domains
        elif inclusion_list and any(incl in domain for incl in inclusion_list):
            included.append(link)  # Add to prioritized list
        else:
            filtered.append(link)

    return {"included": included, "filtered": filtered}
