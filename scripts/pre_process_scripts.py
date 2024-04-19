import spacy
from spacy.tokens import Token

# Load spaCy's language model
nlp = spacy.load("en_core_web_sm")

# Initializing the dictionary
characters = {}

# The name of the specific characters you want to append
specific_characters = ["Space Ghost", "Zorak", "Moltar"]

# Load the lines spoken by Space Ghost
with open("space_ghost_lines.txt", "r") as file:
    space_ghost_lines = file.read().split("\n")

# Load the lines spoken by Zorak
with open("zorak_lines.txt", "r") as file:
    zorak_lines = file.read().split("\n")

# Load the lines spoken by Moltar
with open("moltar_lines.txt", "r") as file:
    moltar_lines = file.read().split("\n")

characters = {"Space Ghost": space_ghost_lines, "Zorak": zorak_lines, "Moltar": moltar_lines}

# Tokenize the lines into words
for character, dialogues in characters.items():
    tokenized_dialogues = []
    for dialogue in dialogues:
        doc = nlp(dialogue)
        tokenized_dialogue = [token.text.lower() for token in doc if not token.is_stop]
        lemmatized_dialogue = [token.lemma_ for token in doc]
        tokenized_dialogues.append(" ".join(lemmatized_dialogue))
    # Save the processed dialogues into separate files for each character
    with open(f"{character}_dialogues.txt", "w") as file:
        file.write("\n".join(tokenized_dialogues))
