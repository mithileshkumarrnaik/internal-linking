import streamlit as st
import pandas as pd
from helpers.scrape import fetch_sitemap_urls, scrape_blog_data
from helpers.process import filter_pages, generate_keywords, suggest_internal_links
from helpers.nltk_setup import ensure_nltk_data

# Ensure NLTK resources are available
ensure_nltk_data()

# Streamlit App
st.title("Content Scraper and Link Suggester")

# Step 1: Sitemap Selection
SITEMAP_OPTIONS = [
    "https://acviss.com/page-sitemap.xml",
    "https://blog.acviss.com/sitemap-post.xml",
    "https://blog.acviss.com/sitemap-home.xml",
]

st.header("Step 1: Select Sitemap")
selected_sitemaps = st.multiselect(
    "Choose one or more sitemaps to crawl:",
    options=SITEMAP_OPTIONS,
    default=SITEMAP_OPTIONS
)

if not selected_sitemaps:
    st.warning("Please select at least one sitemap.")
else:
    if st.button("Fetch URLs"):
        urls = fetch_sitemap_urls(selected_sitemaps)
        if urls:
            st.write(f"Extracted {len(urls)} URLs")
            st.session_state['urls'] = urls
            st.dataframe(urls)
        else:
            st.error("No URLs extracted. Check the sitemap format.")

# Step 2: Scrape Blog Data
st.header("Step 2: Scrape Blog Data")
if "urls" in st.session_state:
    if st.button("Scrape Blogs"):
        scraped_data = scrape_blog_data(st.session_state['urls'])
        scraped_df = pd.DataFrame(scraped_data)
        scraped_df = filter_pages(scraped_df)
        st.session_state['scraped_data'] = scraped_df
        st.write("Filtered Scraped Blog Data")
        st.dataframe(scraped_df)
else:
    st.warning("Please fetch URLs first!")

# Step 3: Extract Keywords
st.header("Step 3: Extract Keywords")
if "scraped_data" in st.session_state:
    if st.button("Generate Keywords"):
        scraped_df = generate_keywords(st.session_state['scraped_data'])
        st.session_state['scraped_data'] = scraped_df
        st.write("Updated Blog Data with Keywords")
        st.dataframe(scraped_df)
else:
    st.warning("Please scrape blogs first!")

# Step 4: Suggest Internal Links
st.header("Step 4: Suggest Internal Links")
if "scraped_data" in st.session_state:
    blog_content = st.text_area("Enter New Blog Content")
    if st.button("Suggest Links"):
        suggestions = suggest_internal_links(blog_content, st.session_state['scraped_data'])
        if not suggestions.empty:
            st.write("Suggested Internal Links")
            st.dataframe(suggestions)
        else:
            st.warning("No relevant links found!")
else:
    st.warning("Please generate keywords first!")
