import json
import os

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.snard.com/sg/guide/"
DATA_FOLDER = "C:/PyGhostal/data/space_ghost_data"


def clean_filename(filename):
    """
    Cleans the input filename by removing invalid characters and leading/trailing spaces.

    Parameters:
    filename (str): The input filename to be cleaned.

    Returns:
    str: The cleaned filename with invalid characters removed.
    """
    return filename.translate(str.maketrans("", "", r'<>:"/\\|?*')).strip()


def get_episode_links(base_url):
    """
    Retrieves episode links from the given base URL using requests and BeautifulSoup.

    Args:
        base_url (str): The base URL to retrieve episode links from.

    Returns:
        list: A list of episode links.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        ep_links = [link["href"] for link in soup.select('a[href^="?ep"]')]
        return ep_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching episode links: {e}")
        return []


def download_episode_text(base_url, episode_url):
    """
    Downloads the text content of a specific episode from the given base URL and episode URL.

    Parameters:
    - base_url (str): The base URL where the episode is located.
    - episode_url (str): The specific URL of the episode to download.

    Returns:
    - str: The text content of the episode.
    """
    full_url = base_url + episode_url
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching episode {episode_url}: {e}")
        return ""


def extract_episode_data(base_url, episode_url):
    """
    Extracts data from a given episode URL by scraping the website.

    Parameters:
    - base_url (str): The base URL of the website.
    - episode_url (str): The URL of the specific episode to extract data from.

    Returns:
    - dict: A dictionary containing the extracted data including title, URL, guest stars, synopsis, and transcript.
    """
    full_url = base_url + episode_url
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.get_text().strip() if soup.title else None
        guest_stars = soup.find("th", string="Guest Stars:").find_next_sibling("td").get_text().strip() if soup.find(
            "th", string="Guest Stars:") else None
        synopsis = soup.find("th", string="Synopsis:").find_next_sibling("td").get_text().strip() if soup.find("th",
                                                                                                               string="Synopsis:") else None
        # Extract transcript
        transcript = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if ":START FEED" not in text and ":" in text:
                speaker, dialogue = text.split(":", 1)
                transcript.append({"speaker": speaker.strip(), "dialogue": dialogue.strip()})

    except requests.exceptions.RequestException as e:
        print(f"Error processing episode {episode_url}: {e}")
        return {}

    return {
        "title": title,
        "url": episode_url,
        "guest_stars": guest_stars,
        "synopsis": synopsis,
        "transcript": transcript,
    }


def save_episode_data(data_folder, episode_data):
    """
    Save the episode data to a file in the specified data folder.

    Args:
        data_folder (str): The folder where the data will be saved.
        episode_data (dict): The data to be saved for the episode.

    Returns:
        None
    """
    if not episode_data:  # Skip empty data
        return

        # Clean up title for filename
    title = episode_data.get("title") or episode_data["url"].replace("?ep=", "episode_")
    filename = clean_filename(title) + ".json"
    filepath = os.path.join(data_folder, filename)

    if os.path.exists(filepath):
        print(f"Episode file {filename} already exists, skipping.")
    else:
        os.makedirs(data_folder, exist_ok=True)  # Create data folder if needed
        with open(filepath, "w") as outfile:
            json.dump(episode_data, outfile, indent=2)  # Indentation for readability


def main():
    """
    A function that fetches episode links, extracts episode data, and saves it.
    """
    episode_links = get_episode_links(BASE_URL)

    for episode_url in episode_links:
        episode_data = extract_episode_data(BASE_URL, episode_url)
        save_episode_data(DATA_FOLDER, episode_data)


if __name__ == "__main__":
    main()
