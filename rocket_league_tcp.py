import socket
import json
import csv
import time
from datetime import datetime

HOST = "127.0.0.1"
PORT = 49123
BUFFER_SIZE = 4096

TRACKED_EVENTS = {
    'MatchInitialized',
    'MatchEnded',
    'StatfeedEvent'
}

TRACKED_EVENT_NAMES = {
    'Assist',
    'Demolish',
    'EpicSave',
    'Goal',
    'OvertimeGoal',
    'Save',
    'Shot'
}

class PlayerStats:
    def __init__(self, username, opp_flag=False, usernames=[]):
        # self.name = name
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
        matched = False

        if event.get('Event') != 'StatfeedEvent':
            return matched
        if not event.get('Data').get('MatchGuid'):
            return matched
        if not event.get('Data').get('MainTarget'):
            return matched

        main_target = event.get('Data').get('MainTarget').get('Name')
        event_name = event.get('Data').get('EventName')

        if self.opp_flag:
            if (main_target not in self.usernames):
                self._handle_event(event_name)
        else:
            if (main_target == self.username):
                self._handle_event(event_name)

    def _handle_event(self, event_name: str):
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
                
    
    def export(self):
        return {
            f'{self.username}_goals':self.goals,
            f'{self.username}_assists':self.assists,
            f'{self.username}_saves':self.saves,
            f'{self.username}_shots':self.shots,
            f'{self.username}_demos':self.demos,
        }

    def reset(self):
        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.shots = 0
        self.demos = 0

    def __str__(self):
        return f'Player: {self.username}\n\tGoals: {self.goals}\n\tShots: {self.shots}\n\tAssists: {self.assists}\n\tSaves: {self.saves}\n\tDemos: {self.demos}'


class GameState:
    def __init__(self, player_usernames: list[str]):
        self.players: list[PlayerStats] = [PlayerStats(username) for username in player_usernames]
        self.opp: PlayerStats = PlayerStats('opp', opp_flag=True, usernames=player_usernames)
        
        self.team_goals = 0
        self.lead = 0
        self.overtime = 0
        self.win = 0
        
        self.game_start = None
        self.game_end = None
        self.game_length = None


    def reset(self):
        self.lead = 0
        self.overtime = 0
        self.win = 0

        self.game_start = None
        self.game_end = None
        self.game_length

        for player in self.players:
            player.reset()
        self.opp.reset()

    
    def export(self):
        game_data = {
            'date':datetime.now().strftime('%Y-%m-%d'),
            'lead':self.lead,
            'overtime':self.overtime,
            'win':self.win,
            'length':self.game_length,
        }

        for player in self.players:
            game_data.update(player.export())
        
        game_data.update(self.opp.export())

        return game_data

        
    def handle_event(self, event: dict):
        event_type = event.get('Event')
        event_timestamp = event.get('Timestamp')

        if event_type == 'MatchInitialized':
            self.reset()
            self.game_start = datetime.strptime(event_timestamp, '%Y-%m-%d_%H-%M-%S')

        elif event_type == 'StatfeedEvent':
            self.opp.handle_event(event)

            for player in self.players:
                player.handle_event(event)

            # Set the team goals in each event
            self.team_goals = sum(player.goals for player in self.players)

            # Set the overtime flag if an overtime goal was scored (only way to know OT started)
            if event.get('Data').get('EventName') == 'OvertimeGoal':
                self.overtime = 1

            # Set the lead flag if the team goals are ever greater than opp goals AND it isn't overtime
            if (self.team_goals > self.opp.goals) and (self.overtime == 0):
                self.lead = 1


        elif event_type == 'MatchEnded':
            self.game_end = datetime.strptime(event_timestamp, '%Y-%m-%d_%H-%M-%S')
            self.game_length = (self.game_end - self.game_start).total_seconds()

            if self.team_goals > self.opp.goals:
                self.win = 1

            game_data = self.export()

            return game_data
        

class RocketLeagueTracker:

    def __init__(self, usernames: list[str]):
        self.events = []
        self.game_states = []
        self.current_state = None

        self.game_state = GameState(usernames)
        self.games = []



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

    def receive(self, s: socket.socket):
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
            
            if event == 'StatfeedEvent':
                event_name = data.get('Data').get('EventName')

                if event_name in TRACKED_EVENT_NAMES:
                    self.events.append(data)
                    print(f'Event: {event_name}')

            else:
                self.events.append(data)
                print(f'Event: {event}')

        # Additional check of when the match ends to append the current state to the game_states
        if event == "MatchEnded":
            if self.current_state:
                self.game_states.append(self.current_state)
            self.current_state = None
            print(f"Game over. Total games: {len(self.game_states)}")


    def compile_data(self):
        for event in self.events:
            game_data = self.game_state.handle_event(event)

            if game_data:
                self.games.append(game_data)
            

    def save_csv(self, filename):
        if self.games:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.games[0].keys())
                writer.writeheader()
                writer.writerows(self.games)
        else:
            print('No Completed games to export')


    def save(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        payload = {"events": self.events, "gameStates": self.game_states}

        filename = f"rl-session-{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved {len(self.events)} events and {len(self.game_states)} game states to {filename}")

        # Build all games and then save to 2 csv files: export.csv (to be rewritten every session) and games-export-{timestamp}.csv (to have a unique csv for each session)
        self.compile_data()

        self.save_csv('export.csv')
        self.save_csv(f'games-export-{timestamp}.csv')
        





if __name__ == "__main__":
    tracker = RocketLeagueTracker(['tekjnbo','ilovethezoo46'])
    try:
        tracker.connect()
    except KeyboardInterrupt:
        tracker.save()
        print("Stopped by user")