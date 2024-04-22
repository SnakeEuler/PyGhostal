import json
import os
import re

from psycopg2._psycopg import DataError
from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.testing.plugin.plugin_base import logging

Base = declarative_base()


def load_config():
    """
    Load the configuration from the 'database_config.json' file.

    This function opens the 'database_config.json' file and reads its contents using the 'json.load' function.
    The contents of the file are then returned as a dictionary.

    Returns:
        dict: The configuration data loaded from the 'database_config.json' file.
    """
    with open('database_config.json', 'r') as config_file:
        db_config = json.load(config_file)
        return db_config


def get_database_config():
    database_config = load_config()['database_config']
    return {'user': database_config['user'], 'password': database_config['password'], 'host': database_config['host'],
            'database': database_config['database']}


def connect_to_db():
    engine_url = (f"postgresql://{get_database_config()['user']}:"
                  f"{get_database_config()['password']}@{get_database_config()['host']}/"
                  f"{get_database_config()['database']}")
    engine = create_engine(engine_url)
    session = sessionmaker(bind=engine)()
    return session


# SQLAlchemy Models

class Action(Base):
    __tablename__ = 'actions'
    action_id = Column(Integer, primary_key=True)
    dialogue_id = Column(Integer, ForeignKey('dialogue.dialogue_id', ondelete="CASCADE"))
    action_type = Column(Text)
    action_description = Column(Text)


class Episode(Base):
    __tablename__ = 'episodes'
    episode_id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    guest_stars = Column(String)
    synopsis = Column(Text)


class Dialogue(Base):
    __tablename__ = 'dialogue'
    dialogue_id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey('episodes.episode_id', ondelete="CASCADE"))
    speaker = Column(String)
    text = Column(Text)
    actions = Column(Text)


class Token(Base):
    __tablename__ = 'tokens'
    token_id = Column(Integer, primary_key=True)
    dialogue_id = Column(Integer, ForeignKey('dialogue.dialogue_id', ondelete="CASCADE"))
    token = Column(Text)
    token_type = Column(Text)


# Action Handling
def extract_actions(dialogue_text):
    """
    Extracts actions from a given dialogue text.

    Args:
        dialogue_text (str): The dialogue text from which to extract actions.

    Returns:
        list: A list of actions found in the dialogue text. Each action is represented as a string.
    """
    action_pattern = r"\((.*?)\)"
    return re.findall(action_pattern, dialogue_text)


def replace_actions_with_placeholder(dialogue_text):
    """
    Replaces actions in the dialogue text with a placeholder string.

    Args:
        dialogue_text (str): The dialogue text containing actions to be replaced.

    Returns:
        str: The dialogue text with actions replaced by the placeholder string.
    """
    return re.sub(r"\(.*?\)", "[Action]", dialogue_text)


def load_episode(session, filepath):
    with open(filepath, 'r') as f:
        episode_data = json.load(f)

    try:
        insert_episode_data(session, episode_data)
    except IntegrityError as e:
        logging.error(f"Error inserting episode (potential duplicate): {filepath}: {e}")
        session.rollback()
    except DataError as e:
        logging.error(f"Error with episode data: {filepath}: {e}")
        session.rollback()


def insert_episode_data(session: Session, episode_data: dict):
    # Insert episode data
    episode = Episode(
        title=episode_data['title'],
        url=episode_data['url'],
        guest_stars=episode_data['guest_stars'],
        synopsis=episode_data['synopsis']
    )
    session.add(episode)
    session.commit()

    # Process each transcript entry
    for transcript_data in episode_data['transcript']:
        insert_transcript_data(session, transcript_data, episode.episode_id)


def insert_transcript_data(session: Session, transcript_data: dict, episode_id: int):
    # Insert dialogue data, including actions (assuming actions stored as text)
    dialogue_text = ' '.join(transcript_data['sentences'])  # Combine sentences for 'text' field
    dialogue = Dialogue(
        episode_id=episode_id,
        speaker=transcript_data['speaker'],
        text=dialogue_text,
        actions='; '.join(transcript_data['actions'])  # Serialize actions with semicolon as delimiter
    )
    session.add(dialogue)
    session.commit()

    # Insert tokens
    insert_tokens(session, dialogue.dialogue_id, transcript_data)


def insert_tokens(session: Session, dialogue_id: int, transcript_data: dict):
    # Insert word and subword tokens (Adapt this based on how you have subword tokens structured)
    for token in transcript_data['words']:
        new_token = Token(
            dialogue_id=dialogue_id,
            token=token,
            token_type='word'
        )
        session.add(new_token)
        session.commit()

    for subword_list in transcript_data['subword_tokens']:
        if isinstance(subword_list, list):
            for subword in subword_list:
                new_token = Token(
                    dialogue_id=dialogue_id,
                    token=subword,
                    token_type='subword'
                )
                session.add(new_token)
                session.commit()
        else:
            new_token = Token(
                dialogue_id=dialogue_id,
                token=subword_list,
                token_type='subword'
            )
            session.add(new_token)
            session.commit()


def main():
    data_folder = "C:/PyGhostal/data/preprocessed_episodes"  # Update to your data location
    session = connect_to_db()

    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(data_folder, filename)
            load_episode(session, filepath)

    session.close()


if __name__ == '__main__':
    main()
