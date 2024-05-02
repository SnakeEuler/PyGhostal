- ## Dev log entry 2: Powerbands vs Data:
	- Putting transcript data into it's place with PostgreSQL.
	-
	  ```
	  -- Here is a relevent dialogue snippit in json for fun. 
	  {
	        "speaker": "Space Ghost",
	        "dialogue": "Moltar! Damage report?"
	      },
	      {
	        "speaker": "Moltar",
	        "dialogue": "(as Star Trek's Scotty) She's breaking up!  She's gonna blow, Space Ghost!"
	      },
	  ```
-
- In my last thrilling episode, I emerged from the digital wilds clutching transcripts from Space Ghost Coast to Coast – chaotic relics of televised absurdity. Now, the quest shifts from collection to categorization. Enter PostgreSQL, a bastion of database might, promising order amidst the madness.
- **The Challenges**
	- Initially, my inner tinkerer toyed with further nesting my JSON data. But such rigidity felt at odds with Space Ghost's unpredictable spirit. Whispers of a database echoed in my mind... PostgreSQL beckoned with its promises of flexible queries and data relationships.
	- Database sketches materialized: `episodes` for metadata, `dialogue` to hold the conversational heart, and... a separate realm for those cryptic 'actions'? Would strict hierarchy prevail, or would the flexibility of JSON columns reign supreme?
- **PostgreSQL Takes Form**
	- After muscling through the initial setup and connectivity hurdles, I hammered out a SQL schema that looked something like this:
	  collapsed:: true
		-
		  ```
		  -- create schema
		  
		  -- episodes table
		  CREATE TABLE episodes
		  (
		      episode_id  SERIAL PRIMARY KEY,
		      title       TEXT,
		      url         TEXT,
		      guest_stars TEXT,
		      synopsis    TEXT
		  );
		  
		  -- dialogue table
		  CREATE TABLE dialogue
		  (
		      dialogue_id SERIAL PRIMARY KEY,
		      episode_id  INTEGER REFERENCES episodes (episode_id) ON DELETE CASCADE,
		      speaker     TEXT,
		      text        TEXT,
		      actions     JSONB
		  );
		  
		  -- tokens table
		  CREATE TABLE tokens
		  (
		      token_id    SERIAL PRIMARY KEY,
		      dialogue_id INTEGER REFERENCES dialogue (dialogue_id) ON DELETE CASCADE,
		      token       TEXT
		  );
		  
		  -- Text Search Index
		  CREATE INDEX dialogue_text_idx ON dialogue USING GIN (text);
		  
		  ```
		- For a quick start, I resorted to trusty `psycopg2`, building a simple helper script to execute my schema.
		- **The SQLAlchemy Shift**
		- The realization hit like a bolt of Space Ghost's Powerbands: investing in SQLAlchemy would pave the way for my chatbot's true potential. With newfound determination, I crafted a loading module and a trusty console interface, allowing me to meticulously test data loading one episode at a time.
		- A past lesson in duplicate mishaps burned bright in my memory. To ensure the integrity of my cosmic tome of Space Ghost wisdom, I swiftly fortified my script against replication:
		- At first I used psycopg2 and made a tiny little helper python file to actually create the schema in the database.
		-
		  ```
		  import psycopg2
		  
		  
		  def create_database_schema(database_config):
		      """
		      Create the database schema by executing the SQL statements from the 'create_schema.sql' file.
		  
		      Args:
		          database_config (dict): A dictionary containing the configuration parameters for the database connection.
		  
		      Returns:
		          None
		      """
		      conn = psycopg2.connect(**database_config)
		      cursor = conn.cursor()
		  
		      with open('create_schema.sql', 'r') as f:
		          sql = f.read()
		          cursor.execute(sql)
		  
		      conn.commit()
		      conn.close()
		  
		  ```
		-
	-
	  ```
	  -- create schema
	  
	  -- episodes table
	  CREATE TABLE episodes
	  (
	      episode_id  SERIAL PRIMARY KEY,
	      title       TEXT,
	      url         TEXT,
	      guest_stars TEXT,
	      synopsis    TEXT
	  );
	  
	  -- dialogue table
	  CREATE TABLE dialogue
	  (
	      dialogue_id SERIAL PRIMARY KEY,
	      episode_id  INTEGER REFERENCES episodes (episode_id) ON DELETE CASCADE,
	      speaker     TEXT,
	      text        TEXT,
	      actions     JSONB
	  );
	  
	  -- tokens table
	  CREATE TABLE tokens
	  (
	      token_id    SERIAL PRIMARY KEY,
	      dialogue_id INTEGER REFERENCES dialogue (dialogue_id) ON DELETE CASCADE,
	      token       TEXT
	  );
	  
	  -- Optional Text Search Index
	  CREATE INDEX dialogue_text_idx ON dialogue USING GIN (text);
	  
	  ```
	- Armed with `psycopg2`, I launched a modest helper script to baptize my schema into being. But then, a bolt of realization from Space Ghost's powerbands struck: embracing SQLAlchemy might unlock the full potential of my chatbot endeavor.
	-
	  ```
	  import psycopg2
	  
	  
	  def create_database_schema(database_config):
	      """
	      Create the database schema by executing the SQL statements from the 'create_schema.sql' file.
	  
	      Args:
	          database_config (dict): A dictionary containing the configuration parameters for the database connection.
	  
	      Returns:
	          None
	      """
	      conn = psycopg2.connect(**database_config)
	      cursor = conn.cursor()
	  
	      with open('create_schema.sql', 'r') as f:
	          sql = f.read()
	          cursor.execute(sql)
	  
	      conn.commit()
	      conn.close()
	  
	  ```
	-
	- ### The SQLAlchemy Epiphany
		- The switch to SQLAlchemy wasn't just a shift—it was a revelation, a moment when the cosmic tumblers clicked into place. This ORM layer between Python and PostgreSQL could elegantly bridge my need for order with the inherent chaos of the data.
		- Haunted by the specter of past duplicate disasters, I fortified my script against replication errors, ensuring each episode's unique identity was preserved in the database.
		- Defining my models with SQLAlchemy's declarative base was like sketching with a fine pen instead of a crayon, sidestepping the crudeness of raw SQL.
	-
	  ```
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
	  ```
	- SQLAlchemy's declarative base proved a revelation! Defining models like `Episode` and `Dialogue` felt natural, their structures mirroring my database tables, saving me from the tedium of raw SQL wrangling.
- **Confronting the Action Enigma**
	- Those enigmatic '(actions)' scattered throughout the transcripts, for example Space Ghost often (invisos to desk), pose a unique puzzle in how to best leverage them for the model and bot outcome. For now, simple pattern matching helps me isolate them. But to truly capture the essence of Space Ghost's absurdity, I may need to summon the power of NLP. spaCy beckons, promising techniques to identify the specific types of actions driving the show's chaotic humor.
- **Uncertainties and the Path Ahead**
	- The best way to tokenize the dialogue remains a delightful mystery. Should I break things down into words, phrases, or whole sentences? And how best to group conversations for training? A rolling window seems like a chaotic (and appropriate) start, but will it capture the true spirit of the show's disjointed brilliance?
	-
	- The journey continues! Armed with a structured database and tantalizing hints of NLP sorcery, I forge ahead. My goal remains clear: to craft a chatbot that echoes the nonsensical genius of Space Ghost, Moltar, and Zorak – a conversational AI worthy of the Phantom Cruiser itself!
- ### Next Episode: Organizing Chaos Tokin by Token with NLP
	- I delve into natural language processing to tease order from the delightful madness of Space Ghost's universe.I'm getting into NLP.
-
