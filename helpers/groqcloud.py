import os
import openai
import pandas as pd
import streamlit as st

# Get OpenAI API key from Streamlit secrets or environment
api_key = st.secrets["openai"]["api_key"] if "openai" in st.secrets else os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def generate_openai_embeddings(blog_df):
    def fetch_embedding(text):
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            return None
    blog_df["embedding"] = blog_df["content"].apply(fetch_embedding)
    return blog_df
