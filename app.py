import streamlit as st
import pandas as pd
from helpers.nltk_setup import setup_nltk_data
from helpers.progress import show_progress

# Ensure NLTK resources are available
setup_nltk_data()

from helpers.scrape import fetch_sitemap_urls, scrape_blog_data
from helpers.process import (
    load_list,
    filter_external_links,
    extract_keywords_with_rake,
    suggest_internal_links,
)
# Define paths for inclusion and exclusion lists
EXCLUSION_FILE = "exclusion_list.txt"
INCLUSION_FILE = "inclusion_list.txt"

# Predefined list of sitemaps
SITEMAP_LINKS = [
    "https://acviss.com/page-sitemap.xml",
    "https://blog.acviss.com/sitemap-post.xml",
    "https://blog.acviss.com/sitemap-home.xml",
]
# Load inclusion and exclusion lists
try:
    exclusion_list = load_list(EXCLUSION_FILE)
    inclusion_list = load_list(INCLUSION_FILE)
except FileNotFoundError as e:
    st.error(f"Error loading lists: {e}")
    exclusion_list = []
    inclusion_list = []

# Add a session state to track progress
if "scraped_data" not in st.session_state:
    st.session_state["scraped_data"] = None
if "new_blog_content" not in st.session_state:
    st.session_state["new_blog_content"] = ""

# Step 1: Scrape URLs
if st.button("Scrape and Process URLs"):
    if not selected_sitemaps:
        st.error("Please select at least one sitemap to process.")
    else:
        all_urls = fetch_sitemap_urls(selected_sitemaps)

        if not all_urls:
            st.error("No URLs extracted. Check sitemap format.")
        else:
            # Filter URLs using exclusion and inclusion lists
            filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

            st.subheader("URL Processing Summary")
            st.write(f"**Excluded URLs:** {len(filtered_links['excluded'])}")
            st.write(f"**Included URLs:** {len(filtered_links['included'])}")
            st.write(f"**Remaining URLs:** {len(filtered_links['filtered'])}")

            st.write("Excluded URLs:")
            st.write(filtered_links['excluded'])


# Step 2: Enter New Blog Content
st.header("Step 2: Enter New Blog Content")
new_blog_content = st.text_area(
    "Paste the new blog content here.",
    value=st.session_state.get("new_blog_content", ""),  # Use session state if content exists
    key="new_blog_content_area"
)

# Save to session state
if new_blog_content:
    st.session_state["new_blog_content"] = new_blog_content

# Step 3: Suggest Relevant URLs
if new_blog_content:
    st.header("Step 3: Suggest Relevant URLs")
    if st.session_state["scraped_data"] is not None:
        suggestions = suggest_internal_links(new_blog_content, st.session_state["scraped_data"])
        if not suggestions.empty:
            st.write("Suggested URLs Based on Keywords")
            st.dataframe(suggestions)
        else:
            st.warning("No relevant URLs found.")
    else:
        st.warning("Please scrape URLs first in Step 1.")
        
# Debug: Print exclusion list and URLs
st.write("Exclusion List:", exclusion_list)
st.write("All URLs:", urls)
