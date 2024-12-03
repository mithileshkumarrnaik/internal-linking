import nltk
import os

def setup_nltk_data():
    """
    Ensures that required NLTK data is downloaded and available.
    """
    nltk_data_path = os.getenv("NLTK_DATA", "/home/adminuser/venv/nltk_data")
    nltk.data.path.append(nltk_data_path)  # Add the custom path for NLTK data

    required_resources = ["stopwords", "punkt"]
    for resource in required_resources:
        try:
            nltk.data.find(f"corpora/{resource}")
        except LookupError:
            print(f"Downloading missing NLTK resource: {resource}")
            nltk.download(resource, download_dir=nltk_data_path)
