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