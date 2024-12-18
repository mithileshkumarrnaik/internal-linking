from helpers.progress import show_progress

# Add progress tracking in the scraping process
if st.button("Scrape and Process URLs"):
    if not selected_sitemaps:
        st.error("Please select at least one sitemap to process.")
    else:
        st.write("Scraping URLs...")
        
        # Wrap the URL fetching process in a progress bar
        def process_item(idx):
            # Simulate processing each sitemap URL
            sitemap = selected_sitemaps[idx]
            return fetch_sitemap_urls([sitemap])
        
        scraped_data = show_progress(len(selected_sitemaps), process_item)
        
        # Flatten the scraped data (each item in scraped_data is a list)
        all_urls = [url for sublist in scraped_data for url in sublist]

        if not all_urls:
            st.error("No URLs extracted. Check sitemap format.")
        else:
            # Filter URLs using exclusion and inclusion lists
            st.write("Filtering URLs...")
            filtered_links = filter_external_links(all_urls, exclusion_list, inclusion_list)

            # Display URL processing summary
            st.subheader("URL Processing Summary")
            st.write(f"**Excluded URLs:** {len(filtered_links['excluded'])}")
            st.write(f"**Included URLs:** {len(filtered_links['included'])}")
            st.write(f"**Remaining URLs:** {len(filtered_links['filtered'])}")
