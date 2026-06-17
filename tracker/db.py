import sqlite3


DB_URI = 'rocket_tracker.db'
EVENT_TABLE_NAME = 'events'


def create_conn():
    '''
    Creates the connection object to the database. Uses the `DB_URI` variable
    and returns the connection object.
    '''
    conn: sqlite3.Connection = sqlite3.connect(DB_URI, check_same_thread=False)

    return conn


def create_table(conn: sqlite3.Connection):
    '''
    Creates the events table in the database if it doesn't exist.

    To be called by `initialize_schema`
    '''
    create_statement = f'CREATE TABLE IF NOT EXISTS {EVENT_TABLE_NAME}'

    columns = [
        ('event_id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('event_type', 'TEXT'),
        ('timestamp', 'TEXT'),
        ('match_guid', 'TEXT'),
        ('event_name', 'TEXT'),
        ('username', 'TEXT')
    ]

    column_definition = '\n(\n'
    for index, (column_name, data_type) in enumerate(columns):
        column_definition += f'{column_name} {data_type}'
        if index + 1 != len(columns):
            column_definition += ',\n'
        else:
            column_definition += '\n'
    column_definition += ')'

    statement = create_statement + column_definition

    conn.execute(statement)


def initialize_schema(conn: sqlite3.Connection):
    '''
    Initialization function, intended to be run after the connection has been established.
    Runs initialization of creating tables, altering tables, etc. Then closes with committing
    changes.

    Current process:

    Executes `create_table`

    Commits changes
    '''
    create_table(conn)

    conn.commit()


def insert_event(conn: sqlite3.Connection, event_dict: dict):
    '''
    Function which takes an Event json and writes it to the events db model.
    '''
    event_type = event_dict.get('Event')
    timestamp = event_dict.get('Timestamp')

    data: dict = event_dict.get('Data')

    match_guid = data.get('MatchGuid')
    event_name = data.get('EventName')
    username = None

    if data.get('MainTarget'):
        username = data.get('MainTarget').get('Name')

    data_tuple = (event_type, timestamp, match_guid, event_name, username)
    conn.execute('INSERT INTO events (event_type, timestamp, match_guid, event_name, username) VALUES (?, ?, ?, ?, ?)', data_tuple)
    conn.commit()