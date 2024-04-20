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
