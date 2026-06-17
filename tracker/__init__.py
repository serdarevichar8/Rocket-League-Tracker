import os
import socket
import json
import csv
import time
from datetime import datetime        

from tracker.player_stats import PlayerStats
from tracker.game_state import GameState
from tracker.session_state import SessionState
from tracker.config import HOST, PORT, BUFFER_SIZE, TRACKED_EVENTS, TRACKED_EVENT_NAMES
from tracker.db import create_conn, initialize_schema, insert_event

class RocketLeagueTracker:

    def __init__(self, usernames: list[str], queue):
        self.db = create_conn()
        initialize_schema(self.db)

        self.queue = queue

        self.events = []
        self.game_states = []
        self.current_state = None

        self.game_state = GameState(usernames)
        self.games = []

        self.session_state = SessionState(usernames)



    def connect(self):
        '''
        Triggers the script to attempt to connect to the TCP Socket. Retries joining after 3 seconds
        if given a Refused or Reset error. The `PORT` is technically editable, but currently available
        only as a hardcoded element in the file. 
        '''
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    print("Connected")
                    self.receive(s)
            except ConnectionRefusedError:
                print("Connection refused — retrying in 3 seconds...")
                time.sleep(3)
            except ConnectionResetError:
                print("Connection lost — retrying in 3 seconds...")
                time.sleep(3)


    def receive(self, s: socket.socket):
        '''
        Listens to the socket and feeds data into JSON Decoder. After this the message is passed to the
        `handle_message` method to be saved. No data manipulation takes place in this method.
        '''
        s.settimeout(1.0)  # wake up every second to allow Ctrl+C to be caught
        buffer = ""
        while True:
            try:
                chunk = s.recv(BUFFER_SIZE).decode("utf-8")
                if not chunk:
                    print("Connection closed — waiting for Rocket League to reopen...")
                    return  # returns to connect(), which retries
                buffer += chunk
                while buffer:
                    try:
                        data, index = json.JSONDecoder().raw_decode(buffer)
                        self.handle_message(data)
                        buffer = buffer[index:].lstrip()
                    except json.JSONDecodeError:
                        break
            except TimeoutError:
                pass  # no data arrived, loop again


    def handle_message(self, data: dict):
        '''
        JSON Dict for each event is handled by adding a timestamp and evaluating whether the event
        is to be saved or ignored. Currently the saved events are stored in a `TRACKED_EVENTS` and
        the specific StatfeedEvent are decided by `TRACKED_EVENT_NAMES`.

        The JSON string arrives with the "Data" key still a string, so that is also converted to
        JSON.

        For UpdateState events, we don't save all of them as they arrive many times. Only the final
        UpdateState event for each game is saved, and this is handled in the final check for MatchEnded
        events where we push the `current_state` to the `game_states` attribute.

        All other tracked events are saved to the `events` attribute, which is converted to a JSON at
        the close of the script in the `save` method.
        '''
        event = data.get("Event")
        data['Timestamp'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Convert the Data into an actual json/dict rather than string version
        # Checks first if the Data json exists and if it's in string form to decode
        if isinstance(data.get("Data"), str):
            data["Data"] = json.loads(data["Data"])

        # If the event is an update state, dont save immediately but save it to current state
        if event == "UpdateState":
            self.current_state = data
            return

        update_gui = False

        # Check if the event is one that should be tracked, then append to list of events
        if event in TRACKED_EVENTS:
            
            if event == 'StatfeedEvent':
                event_name = data.get('Data').get('EventName')

                if event_name in TRACKED_EVENT_NAMES:
                    self.game_state.handle_event(data)
                    data['Seconds_Remaining'] = self.game_state.seconds_remaining

                    self.events.append(data)
                    insert_event(self.db, data)

                    update_gui = True
                    print(f'Event: {event_name}')

            else:
                self.game_state.handle_event(data)
                data['Seconds_Remaining'] = self.game_state.seconds_remaining

                self.events.append(data)
                insert_event(self.db, data)

                update_gui = True
                print(f'Event: {event}')

            
            

        # Additional check of when the match ends to append the current state to the game states and export GameState objects data
        if event == "MatchEnded":
            game_data = self.game_state.export()
            # self.games.append(game_data)

            self.session_state.games.append(game_data)
            self.session_state.update(self.game_state)

            if self.current_state:
                self.game_states.append(self.current_state)
            self.current_state = None

            print(f"Game over. Total games: {len(self.session_state.games)}")

        if update_gui:
            self.queue.put(True)
            

    def save_csv(self, filename, sub_folder=True):
        '''
        Write the `games` attribute (which is a list of dicts) to a csv file by a provided filename.
        Uses the provided `csv` module to reduce dependencies.

        Drops the csvs into the `games_exports` directory, but has an option to not drop into a sub-folder.
        This is used in the case of `export.csv`.
        '''
        if self.session_state.games:
            folder_name = 'games_exports'
            os.makedirs(folder_name, exist_ok=True)

            filepath = f'{folder_name}/{filename}' if sub_folder else filename

            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.session_state.games[0].keys())
                writer.writeheader()
                writer.writerows(self.session_state.games)
        else:
            print('No Completed games to export')


    def save_json(self, filename):
        '''
        Write the `events` and `game_states` attributes to a json file by a provided filename.
        Uses the provided `json` module to reduce dependencies.

        Drops the json into the `events_exports` directory.
        '''
        payload = {"events": self.events, "gameStates": self.game_states}


        folder_name = 'events_exports'
        os.makedirs(folder_name, exist_ok=True)

        with open(f'{folder_name}/{filename}', "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved {len(self.events)} events and {len(self.game_states)} game states to {filename}")


    def save(self):
        '''
        Called at the end of the script, computes and exports all data gathered during the session.

        Writes all saved events to a timestamped JSON, and writes aggregated game data to an
        'export.csv' and timestamped csv.
        '''
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        self.save_json(f"events-export-{timestamp}.json")

        self.save_csv('export.csv', sub_folder=False)
        self.save_csv(f'games-export-{timestamp}.csv')
