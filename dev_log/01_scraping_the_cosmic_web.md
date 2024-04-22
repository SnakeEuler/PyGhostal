- ## Dev Log Entry 1: Scraping the Cosmic Web of Transcripts
- ### Intro
-
  > To build a chatbot in the Shadow of Space Ghost Coast to Coast: Lend me your megabytes. I'm on a quixotic quest to resurrect the ghost of television past: a chatbot modeled after the gloriously nonsensical Space Ghost Coast to Coast. Fueled by equal parts nostalgia and existential dread (because, frankly, what else is there?), this project aims to recreate the bangumi's signature brand of chaotic genius.  
- **The Challenge**
	- The primary challenge involved extracting episode links and the relevant data for each episode from a structured guide page on the Space Ghost Coast to Coast website (https://www.snard.com/sg/guide/). I had to navigate HTML tables and carefully target specific elements to gather titles, guest stars, synopsises, and the unique episode URLs.Were there consistent HTML tags/classes you targeted, or did the structure vary?
	- The guide page is built around a large HTML table (`<table>`). So my code needed to locate the correct table, iterate through rows(`<tr>`) to access each episode's data and then target specific cells (`<td>`) to extract titles, guest star lists, synopses, and the unique URLs for the individual episode transcripts.
-
- Finding Episode Links:
-
  ```
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
  ```
	- This code used the BeautifulSoup selector `'a[href^="?ep"]'` to precisely target all `<a>` tags where the `href` attribute *starts with* '?ep=', efficiently isolating the correct episode links.
- ### Extracting Episode Data
  > I wasn't entirely sure what data I would or could end up using towards the chatbot and wanted to keep things somewhere in the middle of granular and general. Getting the basic information detailed about each episode seemed like the reasonable and straightforward way to go. I **used Requests to fetch web pages and BeautifulSoup to parse the HTML**.  
-
  > After fetching the episode page content, I targeted a specific `<table border="0">` section to extract the relevant data. To extract titles, guest stars, and synopses, I first located their corresponding table headers (`<th>`) and then retrieved the text content of the adjacent table cells (`<td>`).  
- My first attempt ran into a hitch before I realized that the naming convention for the episodes changed after episode 11. This is why I added the helper `clean_filename`, which in hindsight seems like a no-brainer. I went back and forth on the structure of the json file for the speaker and dialogue lines but eventually landed on keeping them in pairs. I think that this will be helpful for training a model in identifying pairs and responses (more on that later).
- After fetching the episode page content, I targeted the main data section using the `soup.find('table', border="0")` selector.
- To extract titles, guest stars, and synopses, I first located their corresponding table headers (`<th>`) and then retrieved the text content of the adjacent table cells (`<td>`).
- My first attempt ran into a hitch before I realized that the naming convention for the episodes changed after episode 11. This is why I added the helper `clean_filename`, which in hindsight seems like a no brainer.
- I went back and forth on the structure of the json file for the speaker and dialogue lines but eventually landed on keeping them in pairs. I think that this will be helpful for training a model in identifying pairs and responses (more on that later).
-
  ```
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
  
          soup = BeautifulSoup(response.content, "html.parser")
          title = soup.title.get_text().strip() if soup.title else None
          guest_stars = soup.find("th", string="Guest Stars:").find_next_sibling("td").get_text().strip() if soup.find(
              "th", string="Guest Stars:") else None
          synopsis = soup.find("th", string="Synopsis:").find_next_sibling("td").get_text().strip() if soup.find("th",
                                                                                                                 string="Synopsis:") else None
          air_date = soup.find("th", string="Original Air Date:").find_next_sibling("td").get_text().strip() if soup.find(
              "th",
              string="Aired:") else None
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
          "air_date": air_date
      }
  ```
	- Titles were found within the `<title>` tag.
	- Guest stars were extracted by first locating the table header ( "<th>Guest Stars:</th>") and then getting the text content of the adjacent table cell (`<td>`).
	- I found the site's conventions for episode numbers inconsistent so I decided to add a leading number to the filenames to help keep track on my end.
- In this inaugural foray into the digital underbrush of the Space Ghost Coast to Coast archives, I've been both detective and archeologist, unearthing the peculiarities of HTML and the whimsical chaos of episode listings. Like stumbling upon a hidden glyph, the discovery of erratic naming conventions provided an unexpected lesson in the fluidity of web data. Now, armed with this newfound knowledge, I venture forth to the next frontier: refining these raw transcripts into a refined potion for training my conversational automaton. In my forthcoming dev log, I shall delineate the alchemy required to transmute this digital ore into the gold of chatbot banter, inching ever closer to bottling the quintessential pandemonium of Space Ghost.
