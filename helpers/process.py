import requests
import xml.etree.ElementTree as ET
import os

def fetch_sitemap_urls(sitemaps):
    """
    Fetches and extracts URLs from a list of sitemap URLs.

    Args:
    - sitemaps (list): List of sitemap URLs.

    Returns:
    - list: List of URLs extracted from the sitemaps.
    """
    urls = []
    for sitemap in sitemaps:
        try:
            response = requests.get(sitemap, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            urls.extend(
                url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            )
        except Exception as e:
            print(f"Error processing sitemap {sitemap}: {e}")
    return urls


def load_list(file_path):
    """
    Loads a list of domains/URLs from a text file.
    Ignores empty lines and comments (#).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Remove empty lines and comments
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


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
