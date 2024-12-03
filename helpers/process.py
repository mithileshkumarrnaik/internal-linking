def filter_external_links(links, exclusion_list, inclusion_list=None):
    """
    Filters links based on exclusion and inclusion lists.

    Args:
    - links (list): List of links to filter.
    - exclusion_list (list): List of domains/URLs to exclude.
    - inclusion_list (list): List of domains/URLs to prioritize (optional).

    Returns:
    - dict: {
        'included': [prioritized links],
        'excluded': [excluded links],
        'filtered': [remaining links]
    }
    """
    included = []
    excluded = []
    filtered = []

    for link in links:
        domain = link.split("/")[2] if "://" in link else link  # Extract domain

        if any(excl in domain for excl in exclusion_list):
            excluded.append(link)  # Add to excluded list
        elif inclusion_list and any(incl in domain for incl in inclusion_list):
            included.append(link)  # Add to prioritized list
        else:
            filtered.append(link)  # Add to remaining links

    return {"included": included, "excluded": excluded, "filtered": filtered}
