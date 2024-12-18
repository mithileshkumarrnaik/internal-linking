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
st.title("Content Scraper and Link Suggester")
st.header("Step 1: Select Sitemaps")

# Ensure selected_sitemaps is defined
selected_sitemaps = st.multiselect(
    "Select one or more sitemaps to process:",
    SITEMAP_LINKS,
    default=SITEMAP_LINKS[:1],  # Preselect the first sitemap
)

if st.button("Scrape and Process URLs"):
    if not selected_sitemaps:
        st.error("Please select at least one sitemap to process.")
    else:
        st.write("Scraping URLs...")

        # Scrape URLs from the selected sitemaps
        all_urls = fetch_sitemap_urls(selected_sitemaps)

        if not all_urls:
            st.error("No URLs extracted. Check sitemap format.")
        else:
            # Filter URLs using exclusion and inclusion lists
            st.write("Filtering URLs...")
            filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

            # Scrape blog content
            st.write("Scraping blog content...")
            blog_data = scrape_blog_data(filtered_links["filtered"])

            # Convert to DataFrame
            blog_df = pd.DataFrame(blog_data)

            if "title" not in blog_df.columns or "content" not in blog_df.columns:
                st.error("Scraped data does not have the required structure. Check scrape_blog_data.")
            else:
                # Extract keywords for each blog
                blog_df["keywords"] = blog_df["content"].apply(extract_keywords_with_rake)

                # Save processed blog data to session state
                st.session_state["scraped_data"] = blog_df

                st.write(f"Successfully processed {len(blog_df)} blogs.")

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

