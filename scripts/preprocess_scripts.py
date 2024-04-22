import json
import re
from pathlib import Path

import spacy
from transformers import AutoTokenizer

# Load NLP models and tokenizers
nlp = spacy.load("en_core_web_sm")
subword_tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")


# Function to determine whether subword tokenization is necessary
def should_apply_subword_tokenization(token):
    return len(token) > 5


# Function to tokenize a single line of dialogue
def tokenize_dialogue_line(dialogue_line):
    doc = nlp(dialogue_line)
    words = [token.text for token in doc]
    sentences = [sent.text for sent in doc.sents]
    noun_phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk) > 1]
    subword_tokens = [
        subword_tokenizer.tokenize(token.text) if should_apply_subword_tokenization(token.text) else token.text for
        token in doc]
    return words, sentences, noun_phrases, subword_tokens


# Preprocess individual dialogue lines
def preprocess_line(dialogue_line):
    dialogue_line = dialogue_line.lower()
    cleaned_line = re.sub(r"[^\w\s]|<[^>]*>|https?:\/\/\S+", "", dialogue_line)
    doc = nlp(cleaned_line)
    lemmas = [token.lemma_ for token in doc if token.text not in nlp.Defaults.stop_words and token.is_ascii]
    entities = [(entity.text, entity.label_) for entity in doc.ents]
    return lemmas, entities


# Extract actions using a precompiled regular expression
action_pattern = re.compile(r"\((.*?)\)")


def extract_actions(dialogue_text):
    return action_pattern.findall(dialogue_text)


# Process each episode's dialogue
def preprocess_episode(episode_data):
    processed_transcript = []
    for turn in episode_data["transcript"]:
        processed_tokens, entities = preprocess_line(turn["dialogue"])
        words, sentences, noun_phrases, subword_tokens = tokenize_dialogue_line(turn["dialogue"])
        processed_turn = {
            "speaker": turn.get("speaker"),
            "actions": extract_actions(turn["dialogue"]),
            "sentences": sentences,
            "words": processed_tokens,
            "phrases": noun_phrases,
            "subword_tokens": subword_tokens,
            "entities": entities
        }
        processed_transcript.append(processed_turn)
    return processed_transcript


# Read, process, and save the processed transcript
def process_file(filepath, output_folder):
    filepath = Path(filepath)
    output_folder = Path(output_folder)
    output_path = output_folder / filepath.name

    if not output_path.exists():
        with filepath.open("r") as file:
            episode_data = json.load(file)
        processed_transcript = preprocess_episode(episode_data)
        episode_data["transcript"] = processed_transcript
        output_folder.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as file:
            json.dump(episode_data, file, indent=2)
    else:
        print(f"Processed file {filepath.name} already exists. Skipping...")


# Main function to process all episodes
def main():
    input_folder = Path("C:/PyGhostal/data/space_ghost_data")
    output_folder = Path("C:/PyGhostal/data/preprocessed_episodes")

    print("Starting preprocessing of episode transcripts...")
    for filename in input_folder.glob("*.json"):
        process_file(input_folder / filename, output_folder)


if __name__ == "__main__":
    main()

