import requests
from bs4 import BeautifulSoup


def get_episode_links(base_url):
    """
    Get episode links from the provided base URL.

    :param base_url: The base URL to extract episode links from.
    :return: A list of episode links.
    """
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [base_url + a['href'] for a in soup.find_all('a') if 'episode' in a['href']]
    return links


def scrape_dialogues(episode_url):
    """
    Scrapes dialogues from the given episode URL and returns a dictionary of character names as keys and their
    respective dialogues as values.

    Parameters:
    episode_url (str): The URL of the episode to scrape dialogues from.

    Returns:
    dict: A dictionary with character names as keys and lists of their dialogues as values.
    """
    response = requests.get(episode_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    dialogues = {}
    for p in soup.find_all('p'):
        if ':' in p.text:
            character, dialogue = p.text.split(':', 1)
            if character.strip() in ['Space Ghost', 'Moltar', 'Zorak']:
                if character.strip() not in dialogues:
                    dialogues[character.strip()] = []
                dialogues[character.strip()].append(dialogue.strip())
    return dialogues
