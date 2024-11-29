import nltk
import os

def ensure_nltk_data():
    """
    Ensures the required NLTK data is available.
    Downloads to a local nltk_data directory if not present.
    """
    nltk_data_path = os.path.join(os.getcwd(), "nltk_data")  # Custom nltk_data directory
    nltk.data.path.append(nltk_data_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(nltk_data_path):
        os.makedirs(nltk_data_path)

    # Ensure punkt and stopwords are downloaded
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', download_dir=nltk_data_path, quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)
