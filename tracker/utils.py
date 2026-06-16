import sqlite3

def insert_event(connection: sqlite3.Connection, event_dict: dict):
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
    connection.execute('INSERT INTO events (event_type, timestamp, match_guid, event_name, username) VALUES (?, ?, ?, ?, ?)', data_tuple)
    connection.commit()