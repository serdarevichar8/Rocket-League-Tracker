import os
import sqlite3
import json


def create_db():
    conn = sqlite3.connect('rocket_tracker.db')

    cur = conn.cursor()

    cur.execute('CREATE TABLE events(event_type, timestamp, match_guid, event_name, username)')

    conn.close()




class Event:
    def __init__(self, event_dict: dict):
        self.event_type = event_dict.get('Event')
        self.timestamp = event_dict.get('Timestamp')

        self.data: dict = event_dict.get('Data')

        self.match_guid = self.data.get('MatchGuid')
        self.event_name = self.data.get('EventName')
        self.username = None

        if self.data.get('MainTarget'):
            self.username = self.data.get('MainTarget').get('Name')

        self.tuple = (self.event_type, self.timestamp, self.match_guid, self.event_name, self.username)
    

    def insert(self, connection:sqlite3.Connection):
        connection.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)', self.tuple)
        connection.commit()



if __name__ == '__main__':
    with open('rl-session-2026-06-01_17-09-12.json') as f:
        data = json.load(f)
        events: list = data.get('events')


    if not os.path.isfile('rocket_tracker.db'):
        create_db()

    with sqlite3.connect('rocket_tracker.db') as conn:
        for i in range(5):
            e = Event(events[i])
            e.insert(conn, conn.cursor())