import socket
import json
import time
from datetime import datetime

HOST = "127.0.0.1"
PORT = 49123
BUFFER_SIZE = 4096

TRACKED_EVENTS = [
    'MatchInitialized',
    'MatchEnded',
    'StatfeedEvent'
]

class PlayerStats:
    def __init__(self, name, username, opp_flag=False, usernames=[]):
        self.name = name
        self.username = username
        self.opp_flag = opp_flag
        self.usernames = usernames

        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.shots = 0
        self.demos = 0

    def add_goal(self):
        self.goals += 1
    
    def add_assist(self):
        self.assists += 1
    
    def add_save(self):
        self.saves += 1
    
    def add_shot(self):
        self.shots += 1
    
    def add_demo(self):
        self.demos += 1

    def handle_event(self, event: dict):
        if not event.get('Data').get('MainTarget') or not event.get('Data').get('MatchGuid') or not event.get('Event') == 'StatfeedEvent':
            return

        main_target = event.get('Data').get('MainTarget').get('Name')
        if (main_target == self.username) or (self.opp_flag and main_target not in self.usernames):
            event_name = event.get('Data').get('EventName')

            if event_name == 'Goal':
                self.add_goal()
            elif event_name == 'Assist':
                self.add_assist()
            elif event_name in ['Save','EpicSave']:
                self.add_save()
            elif event_name == 'Shot':
                self.add_shot()
            elif event_name == 'Demolish':
                self.add_demo()

    def reset(self):
        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.shots = 0
        self.demos = 0

    def __str__(self):
        return f'Player: {self.name}\n\tGoals: {self.goals}\n\tShots: {self.shots}\n\tAssists: {self.assists}\n\tSaves: {self.saves}\n\tDemos: {self.demos}'


class RocketLeagueTracker:

    def __init__(self):
        self.events = []
        self.game_states = []
        self.current_state = None

        # self.player_one_stats = PlayerStats(name=player_one[0], username=player_one[1])
        # self.player_two_stats = PlayerStats(name=player_two[0], username=player_two[1])

    def connect(self):
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

    def receive(self, s):
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

        # Check if the event is one that should be tracked, then append to list of events
        if event in TRACKED_EVENTS:
            self.events.append(data)

            if event == 'StatfeedEvent':
                event_name = data.get('Data').get('EventName')
                print(f'Event: {event_name}')

            else:
                print(f'Event: {event}')

        # Additional check of when the match ends to append the current state to the game_states
        if event == "MatchEnded":
            if self.current_state:
                self.game_states.append(self.current_state)
            self.current_state = None
            print(f"Game over. Total games: {len(self.game_states)}")


    def compile_data(self):
        har_stats = PlayerStats('har', 'tekjnbo')
        kev_stats = PlayerStats('kev', 'ilovethezoo46')
        opp_stats = PlayerStats('opp', 'opp', opp_flag=True, usernames=['tekjnbo','ilovethezoo46'])

        for event in self.events:
            

            har_stats.handle_event(event)
            kev_stats.handle_event(event)
            opp_stats.handle_event(event)
            

        


    def save(self):
        payload = {"events": self.events, "gameStates": self.game_states}
        filename = f"rl-session-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(filename, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved {len(self.events)} events and {len(self.game_states)} game states to {filename}")


if __name__ == "__main__":
    tracker = RocketLeagueTracker()
    try:
        tracker.connect()
    except KeyboardInterrupt:
        tracker.save()
        print("Stopped by user")