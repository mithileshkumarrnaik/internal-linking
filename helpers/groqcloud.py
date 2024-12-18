import os
from groqcloud import GroqClient
import pandas as pd

# Initialize the GroqCloud client
def get_groqcloud_client():
    api_key = os.getenv("GROQCLOUD_API_KEY")  # Secure your API key in environment variables
    client = GroqClient(api_key=api_key)
    return client

# Generate embeddings for blog content using GroqCloud
def generate_groqcloud_embeddings(blog_df):
    client = get_groqcloud_client()

    def fetch_embedding(text):
        response = client.embedding.create(input_text=text)
        return response["embedding"]  # Adjust based on GroqCloud's API response

    # Generate embeddings for blog content
    blog_df["embedding"] = blog_df["content"].apply(fetch_embedding)
    return blog_df
