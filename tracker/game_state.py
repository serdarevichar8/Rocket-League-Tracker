from tracker.player_stats import PlayerStats

from datetime import datetime

class GameState:
    '''
    Object used to track the current state of a game. This holds attributes regarding ONLY the current game.
    The object consumes an event via `handle_event` method and updates itself according to the event. Upon
    a game ending (MatchEnded event), the method will export a dictionary of the game stats. This can be
    appended to a list of games.

    The `players` and `opp` attributes are a list of `PlayerStats` and `PlayerStats` objects respectively.
    The `handle_event` method will faciliate the update of each of these automatically.

    The `reset` method will clear all attributes, to be used when moving from one completed game to a new
    one.

    The `export` method will write the following attributes to a dictionary, and combine it with the attributes
    of each of the `PlayerStats` objects in `players` and `opp`:
    - date: Date timestamp in the format YYYY-MM-DD
    - lead: boolean in integer form whether a lead was ever held
    - overtime: boolean in integer form whether the game went to overtime
    - win: boolean in integer form whether the game was won
    - length: integer number of seconds between game start and end
    '''
    def __init__(self, player_usernames: list[str]):
        self.players: list[PlayerStats] = [PlayerStats(username) for username in player_usernames]
        self.opp: PlayerStats = PlayerStats('opp', opp_flag=True, usernames=player_usernames)
        
        self.team_goals = 0
        self.lead = 0
        self.overtime = 0
        self.win = 0
        self.margin = 0
        
        self.game_start = None
        self.game_end = None
        self.game_length = None
        
        self.seconds_remaining = 300

        self.largest_lead = 0
        self.largest_deficit = 0

        self.win_prob = 50
        self.win_probabilities: list[tuple[int, int]] = [(300, 50)]
        self.max_win_prob = 50
        self.min_win_prob = 50


    def reset(self):
        '''
        Clears all attributes. To be used when moving from a completed game to a new game.
        '''
        self.team_goals = 0
        self.lead = 0
        self.overtime = 0
        self.win = 0
        self.margin = 0

        self.game_start = None
        self.game_end = None
        self.game_length = None

        self.seconds_remaining = 300

        self.largest_lead = 0
        self.largest_deficit = 0

        self.win_prob = 50
        self.win_probabilities = [(300, 50)]
        self.max_win_prob = 50
        self.min_win_prob = 50

        for player in self.players:
            player.reset()
        self.opp.reset()

    
    def export(self):
        '''
        Writes the following attributes to a dictionary, and combines it with the attributes
        of each of the `PlayerStats` objects in `players` and `opp`:
        - date: Date timestamp in the format YYYY-MM-DD
        - lead: boolean in integer form whether a lead was ever held
        - overtime: boolean in integer form whether the game went to overtime
        - win: boolean in integer form whether the game was won
        - length: integer number of seconds between game start and end
        '''
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
        '''
        Consumes an event from the tracker and updates all attributes according to the event:

        - MatchInitialized: Resets all attributes to start fresh, and takes the timestamp snapshot
        - StatfeedEvent: Sends the event to all assosciated `PlayerStats` objects to be handled independently
          - Updates the `team_goals`, `overtime`, and `lead` attributes accordingly
        - MatchEnded: Takes timestamp snapshot to compute game length, and updates the `win` attribute
        '''
        event_type = event.get('Event')
        event_timestamp = event.get('Timestamp')

        if event_type == 'MatchInitialized':
            self.reset()
            self.game_start = datetime.strptime(event_timestamp, '%Y-%m-%d_%H-%M-%S')

        elif event_type == 'ClockUpdatedSeconds':
            event_data: dict = event.get('Data')

            if event_data:
                time_seconds: int = event_data.get('TimeSeconds')
                overtime_flag: bool = event_data.get('bOvertime')

                # Set the seconds_remaining to the negative value if in overtime
                self.seconds_remaining = -time_seconds if overtime_flag else time_seconds

                if overtime_flag:
                    self.overtime = 1

        elif event_type == 'StatfeedEvent':
            self.opp.handle_event(event)

            for player in self.players:
                player.handle_event(event)

            # Set the team goals in each event
            self.team_goals = sum(player.goals for player in self.players)

            self.margin = self.team_goals - self.opp.goals
            if self.margin > 0:
                if self.margin > self.largest_lead:
                    self.largest_lead = self.margin
            elif self.margin < 0:
                if abs(self.margin) > self.largest_deficit:
                    self.largest_deficit = abs(self.margin)

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

            self.win_prob = 100 if self.win else 0

            # game_data = self.export()

            # return game_data