import nltk
import os

def ensure_nltk_data():
    nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
    nltk.data.path.append(nltk_data_path)

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", download_dir=nltk_data_path)
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", download_dir=nltk_data_path)
