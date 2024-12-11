import streamlit as st

def show_progress(total_items, process_item_callback):
    """
    Displays a progress bar in Streamlit while processing items.

    Args:
        total_items (int): Total number of items to process.
        process_item_callback (function): A callback function to process each item.
                                          It should accept the current index and return a result.
    Returns:
        list: Results collected from processing each item.
    """
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx in range(total_items):
        result = process_item_callback(idx)
        results.append(result)

        # Update progress bar and status
        progress_bar.progress((idx + 1) / total_items)
        status_text.text(f"Processing {idx + 1}/{total_items} items...")

    # Clear the status text after completion
    status_text.text("Processing complete!")
    return results
