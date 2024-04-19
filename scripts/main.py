import argparse
import logging

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.snard.com/sg/guide/"


def get_episode_links(base_url):
    """Fetches and extracts episode links from the Space Ghost Coast to Coast guide page.

    Args:
        base_url (str): The base URL of the guide section.

    Returns:
        list: A list of episode URLs (relative to the base URL).
    """

    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        ep_links = soup.find_all("a", href=lambda value: value and value.startswith("?ep"))
        return [link["href"] for link in ep_links]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching episode links: {e}")
        return []


def download_episode_text(episode_url):
    """Downloads and extracts the text content of a Space Ghost episode.

    Args:
        episode_url (str): The URL of the episode.

    Returns:
        str: The raw text content of the episode.
    """
    # ... Implementation for downloading and extracting episode text ...


def main():
    parser = argparse.ArgumentParser(description="Scrape transcripts from Space Ghost Coast to Coast website.")
    parser.add_argument("base_url", nargs="?", default=BASE_URL, help="Base URL of the Space Ghost guide")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)  # Set up basic logging

    episode_links = get_episode_links(args.base_url)

    for episode_url in episode_links:
        episode_text = download_episode_text(episode_url)
        # ... Process and save the episode text ...


if __name__ == "__main__":
    main()
