import streamlit as st
import pandas as pd
from helpers.scrape import fetch_sitemap_urls, scrape_blog_data
from helpers.process import load_list, filter_external_links, extract_keywords_with_rake
from helpers.groqcloud import generate_openai_embeddings

exclusion_list = load_list("exclusion_list.txt")
inclusion_list = load_list("inclusion_list.txt")

# Define default sitemap links
SITEMAP_LINKS = [
    "https://acviss.com/page-sitemap.xml",
    "https://blog.acviss.com/sitemap-post.xml",
    "https://blog.acviss.com/sitemap-home.xml",
]

# Add a Streamlit multiselect for sitemap selection
selected_sitemaps = st.multiselect(
    "Select one or more sitemaps to process:",
    SITEMAP_LINKS,
    default=SITEMAP_LINKS[:1],  # Preselect the first sitemap
)

# Step 1: Scrape and Process Data
if st.button("Scrape and Process URLs"):
    if not selected_sitemaps:
        st.error("Please select at least one sitemap to process.")
    else:
        st.write("Scraping URLs...")
        all_urls = fetch_sitemap_urls(selected_sitemaps)

        if not all_urls:
            st.error("No URLs extracted. Check sitemap format.")
        else:
            st.write("Filtering URLs...")
            filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

            st.write("Scraping blog content...")
            blog_data = scrape_blog_data(filtered_links["filtered"])
            blog_df = pd.DataFrame(blog_data)

            if "title" not in blog_df.columns or "content" not in blog_df.columns:
                st.error("Scraped data does not have the required structure. Check scrape_blog_data.")
            else:
                blog_df["keywords"] = blog_df["content"].apply(extract_keywords_with_rake)
                
                # Generate embeddings using OpenAI
                blog_df = generate_openai_embeddings(blog_df)
                st.session_state["scraped_data"] = blog_df

                st.write(f"Successfully processed {len(blog_df)} blogs.")
