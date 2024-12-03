import os
import streamlit as st
import pandas as pd
from helpers.process import (
    fetch_sitemap_urls,
    load_list,
    filter_external_links,
    extract_keywords_with_rake,
    suggest_internal_links,
    scrape_blog_data
)

# Define paths for inclusion and exclusion lists
EXCLUSION_FILE = "exclusion_list.txt"
INCLUSION_FILE = "inclusion_list.txt"

# Load inclusion and exclusion lists
try:
    exclusion_list = load_list(EXCLUSION_FILE)
    inclusion_list = load_list(INCLUSION_FILE)
except FileNotFoundError as e:
    st.error(f"Error loading lists: {e}")
    exclusion_list = []
    inclusion_list = []

# Step 1: Scrape URLs and Filter
st.title("Content Scraper and Link Suggester")

st.header("Step 1: Scrape URLs and Filter")
sitemaps = st.text_area("Enter sitemap URLs (one per line)", height=100)

if st.button("Scrape URLs"):
    sitemap_list = sitemaps.strip().split("\n")
    all_urls = fetch_sitemap_urls(sitemap_list)
    
    if not all_urls:
        st.error("No URLs extracted. Check sitemap format.")
    else:
        # Scrape content and extract keywords
        scraped_data = scrape_blog_data(all_urls)
        scraped_df = pd.DataFrame(scraped_data)
        scraped_df["keywords"] = scraped_df["content"].apply(extract_keywords_with_rake)
        
        # Filter based on inclusion and exclusion lists
        filtered_links = filter_external_links(scraped_df["url"].tolist(), exclusion_list, inclusion_list)
        included_links = filtered_links["included"]
        excluded_links = filtered_links["excluded"]
        remaining_links = filtered_links["filtered"]

        # Display processed data
        st.subheader("Scraped Data with Keywords")
        st.dataframe(scraped_df)

        st.subheader("URL Processing Summary")
        st.write(f"**Total URLs Scraped:** {len(all_urls)}")
        st.write(f"**Excluded URLs:** {len(excluded_links)}")
        st.write(f"**Included URLs:** {len(included_links)}")
        st.write(f"**Remaining URLs:** {len(remaining_links)}")

        # Store processed data in session state
        st.session_state["scraped_data"] = scraped_df

# Step 2: Enter New Blog Content
st.header("Step 2: Enter New Blog Content")
new_blog_content = st.text_area("Paste the new blog content here.")

# Step 3: Suggest URLs
if new_blog_content:
    st.header("Step 3: Suggest Relevant URLs")
    if "scraped_data" in st.session_state:
        scraped_df = st.session_state["scraped_data"]
        suggestions = suggest_internal_links(new_blog_content, scraped_df)
        
        if not suggestions.empty:
            st.write("Suggested URLs Based on Keywords")
            st.dataframe(suggestions)
        else:
            st.warning("No relevant URLs found.")
    else:
        st.warning("Please scrape URLs first in Step 1.")
