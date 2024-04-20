import json
import os
import re


import spacy

nlp = spacy.load("en_core_web_sm")


def preprocess_episode(episode_data):
    """
    Preprocesses an episode's transcript data to extract speaker information, preprocess dialogue, and identify actions.

    Parameters:
    - episode_data (dict): A dictionary containing the transcript data for the episode.

    Returns:
    - processed_transcript (list): A list of dictionaries, each containing processed information for each dialogue turn.
    """
    current_speaker = None
    processed_transcript = []

    for turn in episode_data["transcript"]:
        current_speaker = None
        dialogues = episode_data.get("transcript", [])

        for turn in dialogues:
            speaker = turn.get("speaker")
            dialogue = turn.get("dialogue")

            if speaker is not None:
                current_speaker = speaker
            if current_speaker is not None:
                # Preprocessing Steps
                dialogue = re.sub(r"\([^)]*\)", "[ACTION]", dialogue).strip()
                doc = nlp(dialogue)
                tokens = [token.text for token in doc]
                processed_transcript.append({
                    "speaker": current_speaker,
                    "text": dialogue,
                    "tokens": tokens,
                    "actions": [m.group(0) for m in re.finditer(r"\[ACTION]", dialogue)]
                })

    return processed_transcript  # Return the processed transcript


def process_file(filepath, output_folder):
    """
    Process a file by preprocessing its content and saving the result to an output folder.

    Args:
        filepath (str): The path to the file to be processed.
        output_folder (str): The path to the folder where the processed file will be saved.

    Returns:
        None
    """
    filename = os.path.basename(filepath)
    output_path = os.path.join(output_folder, filename)

    # Check if preprocessed file already exists
    if os.path.exists(output_path):
        print(f"Preprocessed file {filename} already exists. Skipping...")
        return

    with open(filepath, "r") as f:
        episode_data = json.load(f)

    processed_transcript = preprocess_episode(episode_data)
    episode_data["transcript"] = processed_transcript

    os.makedirs(output_folder, exist_ok=True)  # Create the output folder
    with open(output_path, "w") as f:
        json.dump(episode_data, f, indent=2)


def main():
    """
   This code defines a main function that prompts the user to preprocess files. It allows the user to choose to
   preprocess all files, preprocess one file, quit preprocessing, or retry if an invalid choice is made. The function
   processes .json files from the input_folder and saves the processed data to the output_folder
    """
    print("Preprocessing script starting...")
    input_folder = "C:/PyGhostal/data/space_ghost_data"
    output_folder = "C:/PyGhostal/data/preprocessed_episodes"

    while True:
        choice = input("Preprocess next file? (y/n/all/quit): ")
        if choice.lower() == 'quit':
            break
        elif choice.lower() == 'all':
            for filename in os.listdir(input_folder):
                if filename.endswith(".json"):
                    filepath = os.path.join(input_folder, filename)
                    process_file(filepath, output_folder)
            break  # Exit the loop after processing all
        elif choice.lower() == 'y':
            for filename in os.listdir(input_folder):
                if filename.endswith(".json"):
                    filepath = os.path.join(input_folder, filename)
                    process_file(filepath, output_folder)
                    break  # Process one file and go back to the prompt
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
