import os
import streamlit as st
import pandas as pd
from helpers.process import fetch_sitemap_urls, load_list, filter_external_links

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

# Step 4: Sitemap Scraping and Link Filtering
st.header("Step 4: Sitemap Scraping and Link Filtering")

sitemaps = st.text_area("Enter sitemap URLs (one per line)", height=100)

if st.button("Scrape and Process URLs"):
    # Fetch URLs from the sitemap
    sitemap_list = sitemaps.strip().split("\n")
    all_urls = fetch_sitemap_urls(sitemap_list)
    
    if not all_urls:
        st.error("No URLs extracted from the sitemap. Check the sitemap format.")
    else:
        # Process URLs using inclusion and exclusion lists
        filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

        # Calculate totals
        total_urls = len(all_urls)
        excluded_urls = len(filtered_links["excluded"])
        included_urls = len(filtered_links["included"])
        remaining_urls = len(filtered_links["filtered"])

        # Display summary
        st.subheader("URL Processing Summary")
        st.write(f"**Total URLs Scraped:** {total_urls}")
        st.write(f"**Excluded URLs:** {excluded_urls}")
        st.write(f"**Included URLs:** {included_urls}")
        st.write(f"**Remaining URLs:** {remaining_urls}")

        # Display categorized URLs
        st.subheader("Excluded URLs")
        st.write(filtered_links["excluded"])

        st.subheader("Included URLs (Prioritized)")
        st.write(filtered_links["included"])

        st.subheader("Remaining URLs")
        st.write(filtered_links["filtered"])
