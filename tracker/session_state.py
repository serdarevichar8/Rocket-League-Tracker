from tracker.player_stats import PlayerStats
from tracker.game_state import GameState

from statistics import mean

class SessionState:
    def __init__(self, usernames: list[str]):
        self.usernames: list[str] = usernames
        self.players: dict[str, PlayerStats] = {username:PlayerStats(username) for username in self.usernames}
        self.opp: PlayerStats = PlayerStats('opp', opp_flag=True, usernames=self.usernames)

        self.wins: int = 0
        self.losses: int = 0
        self.streak: int = 0
        self.leads: int = 0

        self.ot_wins: int = 0
        self.ot_losses: int = 0

        self.avg_game_length: int = 0

        self.games: list[dict[str]] = []


    def update(self, game_state: GameState):
        self.wins = sum(1 for game in self.games if game.get('win') == 1)
        self.losses = sum(1 for game in self.games if game.get('win') == 0)
        self.leads = sum(game.get('lead') for game in self.games)

        self.ot_wins = sum(1 for game in self.games if game.get('win') == 1 and game.get('overtime') == 1)
        self.ot_losses = sum(1 for game in self.games if game.get('win') == 0 and game.get('overtime') == 1)

        self.avg_game_length = int(mean(game.get('length') for game in self.games))

        for player in  game_state.players:
            username = player.username

            player_session = self.players.get(username)

            if player_session:
                player_session.goals += player.goals
                player_session.assists += player.assists
                player_session.saves += player.saves
                player_session.shots += player.shots
                player_session.demos += player.demos
        
        self.opp.goals += game_state.opp.goals
        self.opp.assists += game_state.opp.assists
        self.opp.saves += game_state.opp.saves
        self.opp.shots += game_state.opp.shots
        self.opp.demos += game_state.opp.demos

        streak = 0

        if len(self.games) > 0:
            games = self.games[::-1]
            last_result = games[0].get('win')

            for game in games:
                if last_result == game.get('win'):
                    streak += 1
                else:
                    break
        
        self.streak = streak if last_result == 1 else -streak