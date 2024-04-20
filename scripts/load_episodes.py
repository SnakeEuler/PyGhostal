import json
import os

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# Connect to your database
def connect_to_db():
    database_config = {
        'user': 'postgres',
        'password': 'aaD',
        'host': 'localhost',
        'database': 'ghostbase'
    }

    engine_url = 'postgresql://{user}:{password}@{host}/{database}'.format(**database_config)
    engine = create_engine(engine_url)
    session = sessionmaker(bind=engine)
    return session()


class Episode(Base):
    __tablename__ = 'episodes'
    episode_id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    guest_stars = Column(String)
    synopsis = Column(Text)


def insert_episode(session, episode_data):
    existing_episode = session.query(Episode).filter_by(title=episode_data['title']).first()

    if existing_episode is None:  # Episode doesn't exist yet
        new_episode = Episode(
            title=episode_data['title'],
            url=episode_data['url'],
            guest_stars=episode_data['guest_stars'],
            synopsis=episode_data['synopsis']
        )
        session.add(new_episode)
        session.commit()
    else:
        for key, value in episode_data.items():
            setattr(existing_episode, key, value)
        session.commit()


def load_episode(session, filepath):
    """
    Loads an episode data from a file specified by the filepath and inserts it into the database session.

    Parameters:
        session (Session): The SQLAlchemy session object used to interact with the database.
        filepath (str): The path to the file containing the episode data.

    Returns:
        None
    """
    with open(filepath, 'r') as f:
        episode_data = json.load(f)

    insert_episode(session, episode_data)


def main():
    data_folder = "C:/PyGhostal/data/preprocessed_episodes"  # Update with your folder path

    session = connect_to_db()

    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            load_episode(session, os.path.join(data_folder, filename))

    session.close()


if __name__ == '__main__':
    main()
