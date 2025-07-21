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
    progress_bar = st.progress(0)
    status_text = st.empty()
    if not selected_sitemaps:
        st.error("Please select at least one sitemap to process.")
    else:
        status_text.text("Scraping URLs...")
        progress_bar.progress(0.1)
        all_urls = fetch_sitemap_urls(selected_sitemaps)

        if not all_urls:
            st.error("No URLs extracted. Check sitemap format.")
            progress_bar.progress(1.0)
        else:
            status_text.text("Filtering URLs...")
            progress_bar.progress(0.3)
            filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

            status_text.text("Scraping blog content...")
            progress_bar.progress(0.5)
            blog_data = scrape_blog_data(filtered_links["filtered"])
            blog_df = pd.DataFrame(blog_data)

            if "title" not in blog_df.columns or "content" not in blog_df.columns:
                st.error("Scraped data does not have the required structure. Check scrape_blog_data.")
                progress_bar.progress(1.0)
            else:
                status_text.text("Extracting keywords...")
                progress_bar.progress(0.7)
                blog_df["keywords"] = blog_df["content"].apply(extract_keywords_with_rake)
                
                status_text.text("Generating embeddings...")
                progress_bar.progress(0.85)
                blog_df = generate_openai_embeddings(blog_df)
                st.session_state["scraped_data"] = blog_df

                status_text.text(f"Successfully processed {len(blog_df)} blogs.")
                progress_bar.progress(1.0)

# --- Internal Linking Suggestion Section ---
if "scraped_data" in st.session_state and not st.session_state["scraped_data"].empty:
    st.header("Suggest Internal Links for New Blog Content")
    new_content = st.text_area(
        "Paste your new blog content here:",
        height=200,
        key="new_blog_content_area"
    )
    if st.button("Suggest Internal Links"):
        from helpers.process import suggest_internal_links, extract_keywords_with_rake
        blog_df = st.session_state["scraped_data"].copy()
        suggestions = suggest_internal_links(new_content, blog_df)
        # Merge keywords from blog_df into suggestions using url
        suggestions = suggestions.merge(blog_df[["url", "keywords"]], on="url", how="left")
        # Extract top similar keywords for each suggestion
        def get_top_keywords(row, new_content):
            existing_keywords = set(str(row["keywords"]).split(", "))
            new_keywords = set(extract_keywords_with_rake(new_content).split(", "))
            return ", ".join(existing_keywords & new_keywords)
        suggestions = suggestions.copy()
        suggestions["top_similar_keywords"] = suggestions.apply(lambda row: get_top_keywords(row, new_content), axis=1)
        st.write("### Suggested Internal Links:")
        st.dataframe(suggestions[["title", "url", "relevance (%)", "top_similar_keywords"]].rename(columns={"relevance (%)": "score"}))
