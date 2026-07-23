import customtkinter as ctk

from tracker import GameState, SessionState, RocketLeagueTracker
from gui.frames.player_frame import PlayerFrame
from gui.frames.score_frame import ScoreFrame
from gui.frames.game_stats_frame import GameStatsFrame
from gui.frames.win_prob_frame import WinProbFrame
from gui.frames.current_game_player_frame import CurrentGamePlayerFrame
from gui.frames.session_mini_cards_frame import SessionMiniCardsFrame
from gui.frames.session_stats_frame import SessionStatsFrame
from gui.frames.session_latest_games_frame import SessionLatestGamesFrame
from gui.frames.config import RED, GREEN


class TrackingPage(ctk.CTkFrame):
    def __init__(self, parent, usernames: list[str], on_save, on_toggle_model):
        super().__init__(parent)

        # single row, three equal columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # three invisible column frames
        self.player_col = ctk.CTkFrame(self, fg_color="transparent")
        self.player_col.grid(row=0, column=0, sticky="nsew")

        self.game_col = ctk.CTkFrame(self, fg_color="transparent")
        self.game_col.grid(row=0, column=1, sticky="nsew")

        self.session_col = ctk.CTkFrame(self, fg_color="transparent")
        self.session_col.grid(row=0, column=2, sticky="nsew")


        self.player_frames: dict[str, PlayerFrame] = {}
        for i, username in enumerate(usernames):
            player_frame = PlayerFrame(self.player_col, username)
            player_frame.pack(fill='x', padx=5, pady=5)

            self.player_frames[username] = (player_frame)

        self.score_frame = ScoreFrame(self.game_col)
        self.score_frame.pack(fill='x', padx=5, pady=5)

        self.game_stats_frame = GameStatsFrame(self.game_col)
        self.game_stats_frame.pack(fill='x', padx=5, pady=5)

        self.win_prob_frame = WinProbFrame(self.game_col)
        self.win_prob_frame.pack(fill='x', padx=5, pady=5)

        self.current_game_player_frame = CurrentGamePlayerFrame(self.game_col, usernames)
        self.current_game_player_frame.pack(fill='x', padx=5, pady=5)

        self.session_mini_cards_frame = SessionMiniCardsFrame(self.session_col)
        self.session_mini_cards_frame.pack(fill='x', padx=5, pady=5)

        self.session_stats_frame = SessionStatsFrame(self.session_col)
        self.session_stats_frame.pack(fill='x', padx=5, pady=5)

        self.session_latest_games_frame = SessionLatestGamesFrame(self.session_col)
        self.session_latest_games_frame.pack(fill='x', padx=5, pady=5)


        self.save_button = ctk.CTkButton(self.session_col, text='Save Data', command=on_save)
        self.save_button.pack()


        self.model_button = ctk.CTkButton(self.game_col, text='Toggle Model', command=on_toggle_model)
        self.model_button.pack()

        # self.test_button = ctk.CTkButton(self.session_col, text='test', command=self.test_visual)
        # self.test_button.pack()


    def update(
            self,
            tracker: RocketLeagueTracker,
            game_state: GameState,
            session_state: SessionState
        ):
        self.score_frame.update(game_state)
        self.game_stats_frame.update(game_state)
        self.win_prob_frame.update(game_state)
        self.current_game_player_frame.update(game_state)

        self.session_mini_cards_frame.update(session_state)
        self.session_stats_frame.update(session_state)
        self.session_latest_games_frame.update(session_state)

        # Loop through the players in the GameState and find their corresponding PlayerFrame
        for username, player_stats in session_state.players.items():
            player_frame = self.player_frames.get(username)

            if player_frame:
                player_frame.update(player_stats, session_state)

        # Update toggle model button - could be done in a separete model in future
        if tracker.model:
            if tracker.model_active:
                self.model_button.configure(fg_color=GREEN)
            else:
                self.model_button.configure(fg_color=RED)
        else:
            self.model_button.configure(state='disabled')






    def test_visual(self):
        game_state = GameState(['tekjnbo', 'ilovethezoo46'])
        game_state.team_goals = 3
        game_state.lead = 1
        game_state.overtime = 0
        game_state.win = 0
        game_state.largest_lead = 2
        game_state.largest_deficit = 1

        game_state.opp.goals = 1
        game_state.players[0].goals = 2
        game_state.players[0].saves = 5
        game_state.players[0].demos = 2

        game_state.players[1].goals = 1
        game_state.players[1].saves = 1
        game_state.players[1].demos = 4

        session_state = SessionState(['tekjnbo', 'ilovethezoo46'])

        session_state.wins = 3
        session_state.losses = 4
        session_state.streak = -2
        session_state.leads = 5
        session_state.ot_wins = 1
        session_state.ot_losses = 0

        har = session_state.players.get('tekjnbo')
        har.goals = 12
        har.assists = 8
        har.saves = 20
        har.shots = 40
        har.demos = 14

        kev = session_state.players.get('ilovethezoo46')
        kev.goals = 15
        kev.assists = 2
        kev.saves = 15
        kev.shots = 50
        kev.demos = 1

        self.update(game_state, session_state)
