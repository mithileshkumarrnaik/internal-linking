import nltk
import os
nltk.download('punkt_tab')

def setup_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    """
    Ensures that required NLTK data is downloaded and available.
    """
    # Define a writable path for NLTK data
    nltk_data_path = os.path.expanduser("~/nltk_data")
    nltk.data.path.append(nltk_data_path)  # Add the custom path for NLTK data

    # Required resources
    required_resources = ["stopwords", "punkt"]
    for resource in required_resources:
        try:
            nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
        except LookupError:
            print(f"Downloading missing NLTK resource: {resource}")
            nltk.download(resource, download_dir=nltk_data_path)

    print("NLTK setup complete. Resources are available.")
