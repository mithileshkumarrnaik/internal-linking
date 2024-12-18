import os
from groqcloud import GroqClient

# Initialize the GroqCloud client
def get_groqcloud_client():
    api_key = os.getenv("GROQCLOUD_API_KEY")  # Or use Streamlit secrets
    client = GroqClient(api_key=api_key)
    return client
