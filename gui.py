import os
import threading
import queue
import json
from typing import Any

import customtkinter as ctk

from tracker import PlayerStats, GameState, SessionState, RocketLeagueTracker

RED = '#e77e7e'
GREEN = '#88cc66'
DARK_GRAY = 'gray90'
CARD_COLOR = "gray20"
CARD_HEADING_FONT = ('default', 16, 'bold')


class StatRow(ctk.CTkFrame):
    def __init__(self, parent, label: str, columns: list[tuple[str, Any]] = [('int', 0)]):
        super().__init__(parent, fg_color="transparent")

        self.columnconfigure(0, weight=1)  # label takes remaining space

        self.label = ctk.CTkLabel(self, text=label, text_color="gray")
        self.label.grid(row=0, column=0, sticky="w")

        self.value_labels: list[ctk.CTkLabel] = []
        for index, column_tuple in enumerate(columns):
            data_type, initial_value = column_tuple

            value_label = ctk.CTkLabel(self, text='', anchor='center', width=40)
            value_label.grid(row=0, column=(index + 1), padx=(0, 0), sticky="e")

            self.value_labels.append((value_label, data_type))

        initial_values = [initial_value for data_type, initial_value in columns]
        self.update(*initial_values)


    def update(self, *args):
        '''
        Updates the values in the statrow, leaves the label the same.

        Takes any number of positional arguments, will take them in the same order as the value labels.

        Make sure to only enter the same number of arguments as values in the statrow.
        '''
        if len(self.value_labels) != len(args):
            raise ValueError('The number of arguments must be equal to the number of values added to the statrow')

        for index, value in enumerate(args):
            value_label, data_type = self.value_labels[index]
            value_label: ctk.CTkLabel

            if data_type == 'int':
                if not isinstance(value, int):
                    raise ValueError(f'Stat row value must be an int, value passed was {value}')
                
                value_label.configure(text=str(value))

            elif data_type == 'float':
                if not isinstance(value, float):
                    raise ValueError(f'Stat row value must be a float, value passed was {value}')
                
                value_label.configure(text=str(round(value, 1)))

            elif data_type == 'bool':
                if value not in (0, 1):
                    raise ValueError(f'Stat row value must be either 0 or 1, value passed was {value}')
                
                bool_text = 'Yes' if value else 'No'
                bool_color = GREEN if value else RED

                value_label.configure(text=bool_text, text_color=bool_color)

            elif data_type == 'pct':
                if not isinstance(value, int):
                    raise ValueError(f'Stat row value must be an int, value passed was {value}')
                
                value_label.configure(text=f'{value}%')


class PlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, username: str, opp=False):
        super().__init__(parent, fg_color=CARD_COLOR)

        self.username = username

        # header row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))
        header_row.columnconfigure(0, weight=1)

        ctk.CTkLabel(header_row, text=username, font=CARD_HEADING_FONT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_row, text="total", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=1)
        # ctk.CTkLabel(header_row, text="/game", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=2, padx=(16, 0))
        ctk.CTkLabel(header_row, text="/game", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=2)

        # divider
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        # stat rows — each needs the same column widths
        self.goals_row   = StatRow(self, "Goals", columns=[('int', 0),('float', 0.0)])
        self.assists_row = StatRow(self, "Assists", columns=[('int', 0),('float', 0.0)])
        self.saves_row   = StatRow(self, "Saves", columns=[('int', 0),('float', 0.0)])
        self.shots_row   = StatRow(self, "Shots", columns=[('int', 0),('float', 0.0)])
        self.demos_row   = StatRow(self, "Demos", columns=[('int', 0),('float', 0.0)])

        for row in (self.goals_row, self.assists_row, self.saves_row, self.shots_row, self.demos_row):
            row.pack(fill="x", padx=12, pady=2)

    def update(self, player_stats: PlayerStats, session_state: SessionState):

        divisor = len(session_state.games) if len(session_state.games) > 0 else 1

        self.goals_row.update(player_stats.goals, player_stats.goals / divisor)
        self.assists_row.update(player_stats.assists, player_stats.assists / divisor)
        self.saves_row.update(player_stats.saves, player_stats.saves / divisor)
        self.shots_row.update(player_stats.shots, player_stats.shots / divisor)
        self.demos_row.update(player_stats.demos, player_stats.demos / divisor)


class ScoreFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        ctk.CTkLabel(self, text="Score", font=CARD_HEADING_FONT).pack(anchor="w", padx=12, pady=(10, 0))
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        score_row = ctk.CTkFrame(self, fg_color="transparent")
        score_row.pack(pady=10)

        self.team_score = ctk.CTkLabel(score_row, text="0", font=("default", 56, 'bold'))
        self.team_score.pack(side="left", padx=16)

        ctk.CTkLabel(score_row, text="—", font=("default", 24), text_color="gray").pack(side="left")

        self.opp_score = ctk.CTkLabel(score_row, text="0", font=("default", 56, 'bold'))
        self.opp_score.pack(side="left", padx=16)

        # label_row = ctk.CTkFrame(self, fg_color="transparent")
        # label_row.pack(fill="x", padx=28, pady=(0, 10))

        # ctk.CTkLabel(label_row, text="team", text_color="gray", font=("default", 11)).pack(side="left")
        # ctk.CTkLabel(label_row, text="opp", text_color="gray", font=("default", 11)).pack(side="right")


    def update(self, game_state: GameState):
        self.team_score.configure(text=str(game_state.team_goals))
        self.opp_score.configure(text=str(game_state.opp.goals))


class GameStatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        ctk.CTkLabel(self, text="Game stats", font=CARD_HEADING_FONT).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.largest_lead = StatRow(self, "Largest lead", columns=[('int', 0)])
        self.largest_deficit = StatRow(self, "Largest deficit", columns=[('int', 0)])
        self.lead_flag = StatRow(self, "Lead at any point", columns=[('bool', 0)])
        self.ot_flag = StatRow(self, "Overtime", columns=[('bool', 0)])

        for row in (self.largest_lead, self.largest_deficit, self.lead_flag, self.ot_flag):
            row.pack(fill="x", padx=12, pady=2)

    def update(self, game_state: GameState):
        self.largest_lead.update(game_state.largest_lead)
        self.largest_deficit.update(game_state.largest_deficit)
        self.lead_flag.update(game_state.lead)
        self.ot_flag.update(game_state.overtime)


class CurrentGamePlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, usernames: list[str]):
        super().__init__(parent, fg_color=CARD_COLOR)

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))
        header_row.columnconfigure(0, weight=1)

        ctk.CTkLabel(header_row, text="This game", font=CARD_HEADING_FONT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_row, text="goals", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=1)
        ctk.CTkLabel(header_row, text="saves", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=2)
        ctk.CTkLabel(header_row, text="demos", text_color="gray", font=("default", 11), anchor='center', width=40).grid(row=0, column=3)

        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.player_rows: dict[str, StatRow] = {}
        for username in usernames:
            row = StatRow(self, username, columns=[('int', 0),('int', 0),('int', 0)])
            row.pack(fill="x", padx=12, pady=2)
            self.player_rows[username] = row


    def update(self, game_state: GameState):
        for player in game_state.players:
            if player.username in self.player_rows:
                player_row = self.player_rows.get(player.username)

                player_row.update(player.goals, player.saves, player.demos)


class MiniCard(ctk.CTkFrame):
    def __init__(self, parent, label: str, value, color = 'white'):
        super().__init__(parent, fg_color=CARD_COLOR)

        self.label = label
        self.value = value

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(4, 0))

        ctk.CTkLabel(header_row, text=self.label, text_color='gray').grid(row=0, column=0, sticky='w')

        self.value_label = ctk.CTkLabel(self, text=self.value, text_color=color, font=("default", 36, 'bold'))
        self.value_label.pack(padx=16, pady=(0, 4), side='left')

    
    def update(self, value, color = None):
        self.value = value
        self.value_label.configure(text=str(self.value))
        if color:
            self.value_label.configure(text_color=color)


class SessionMiniCardsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.wins_card = MiniCard(self, 'Wins', 0, GREEN)
        self.wins_card.grid(row=0, column=0, padx = (0, 5), pady = (0, 5), sticky='ew')

        self.losses_card = MiniCard(self, 'Losses', 0, RED)
        self.losses_card.grid(row=0, column=1, padx = (5, 0), pady = (0, 5), sticky='ew')

        self.streak_card = MiniCard(self, 'Streak', 0)
        self.streak_card.grid(row=1, column=0, padx = (0, 5), pady = (5, 0), sticky='ew')

        self.games_card = MiniCard(self, 'Games', 0)
        self.games_card.grid(row=1, column=1, padx = (5, 0), pady = (5, 0), sticky='ew')


    def update(self, session_state: SessionState):
        self.wins_card.update(str(session_state.wins))
        self.losses_card.update(str(session_state.losses))
        self.games_card.update(str(session_state.wins + session_state.losses))

        if session_state.streak > 0:
            self.streak_card.update(str(session_state.streak), color=GREEN)
        elif session_state.streak < 0:
            self.streak_card.update(str(session_state.streak), color=RED)
        else:
            self.streak_card.update(str(session_state.streak), color='white')


class SessionStatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))
        # header_row.columnconfigure(0, weight=1)

        ctk.CTkLabel(header_row, text="Session Stats", font=CARD_HEADING_FONT).grid(row=0, column=0, sticky="w")
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.win_rate = StatRow(self, "Win Rate", columns=[('pct', 0)])
        self.lead_conversion = StatRow(self, "Lead Conversion", columns=[('pct', 0)])
        self.ot_rate = StatRow(self, "OT Win Rate", columns=[('pct', 0)])
        self.game_length = StatRow(self, "Avg Game Length (s)", columns=[('int', 0)])
        self.avg_opp_goals = StatRow(self, 'Avg Opp G/g', columns=[('float', 0.0)])
        self.goal_differential = StatRow(self, "Goal Differential", columns=[('int', 0)])
        self.save_rate = StatRow(self, 'Save Rate (saves / saves+goals)', columns=[('pct', 0)])
        self.shooting_accuracy = StatRow(self, 'Shooting Accuracy', columns=[('pct', 0)])
        self.assist_rate = StatRow(self, 'Assist Rate', columns=[('pct', 0)])
        self.demo_ratio = StatRow(self, 'Demo Ratio', columns=[('float', 0.0)])

        for row in (
            self.win_rate,
            self.lead_conversion,
            self.ot_rate,
            self.game_length,
            self.avg_opp_goals,
            self.goal_differential,
            self.save_rate,
            self.shooting_accuracy,
            self.assist_rate,
            self.demo_ratio,
        ):
            row.pack(fill="x", padx=12, pady=2)

    
    def update(self, session_state: SessionState):
        games = session_state.wins + session_state.losses
        team_goals = sum(player.goals for player in session_state.players.values())
        team_shots = sum(player.shots for player in session_state.players.values())
        team_saves = sum(player.saves for player in session_state.players.values())
        team_assists = sum(player.assists for player in session_state.players.values())
        team_demos = sum(player.demos for player in session_state.players.values())

        divisor = games or 1
        win_rate = int(session_state.wins / divisor * 100)

        lead_divisor = session_state.leads or 1
        lead_rate = int(session_state.wins / lead_divisor * 100)

        ot_divisor = (session_state.ot_wins + session_state.ot_losses) or 1
        ot_rate = int(session_state.ot_wins / ot_divisor * 100)

        goal_differential = team_goals - session_state.opp.goals

        save_divisor = (session_state.opp.goals + team_saves) or 1
        save_rate = int(team_saves / save_divisor * 100)

        shots_divisor = team_shots or 1
        shooting_accuracy = int(team_goals / shots_divisor * 100)

        assist_divisor = team_goals or 1
        assist_rate = int(team_assists / assist_divisor * 100)

        demo_divisor = session_state.opp.demos or 1
        demo_ratio = team_demos / demo_divisor

        self.win_rate.update(win_rate)
        self.lead_conversion.update(lead_rate)
        self.ot_rate.update(ot_rate)
        self.game_length.update(session_state.avg_game_length)
        self.avg_opp_goals.update(session_state.opp.goals / divisor)
        self.goal_differential.update(goal_differential)
        self.save_rate.update(save_rate)
        self.shooting_accuracy.update(shooting_accuracy)
        self.assist_rate.update(assist_rate)
        self.demo_ratio.update(demo_ratio)


class Square(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color='transparent', border_color='gray30', border_width=1, height=20, width=20)


    def update(self, result = None):
        if isinstance(result, dict):
            result = result.get('win')

        if result == 1:
            self.configure(fg_color=GREEN)
        elif result == 0:
            self.configure(fg_color=RED)


class SessionLatestGamesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(header_row, text="Last 10 Games", font=CARD_HEADING_FONT).grid(row=0, column=0, sticky="w")
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        squares_row = ctk.CTkFrame(self, fg_color="transparent")
        squares_row.pack(pady=(10, 4))

        self.squares = [Square(squares_row, 1) for _ in range(10)]
        for index, square in enumerate(self.squares):
            square.grid(row=0, column=index, padx=5, pady=(0, 4))


    def update(self, session_state: SessionState):
        results = session_state.games[-10:][::-1]

        for index, result in enumerate(results):
            self.squares[index].update(result)







class TrackingPage(ctk.CTkFrame):
    def __init__(self, parent, usernames: list[str], on_save):
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


        # self.test_button = ctk.CTkButton(self.session_col, text='test', command=self.test_visual)
        # self.test_button.pack()


    def update(
            self,
            game_state: GameState,
            session_state: SessionState
        ):
        self.score_frame.update(game_state)
        self.game_stats_frame.update(game_state)
        self.current_game_player_frame.update(game_state)

        self.session_mini_cards_frame.update(session_state)
        self.session_stats_frame.update(session_state)
        self.session_latest_games_frame.update(session_state)

        # Loop through the players in the GameState and find their corresponding PlayerFrame
        for username, player_stats in session_state.players.items():
            player_frame = self.player_frames.get(username)

            if player_frame:
                player_frame.update(player_stats, session_state)






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











class HomePage(ctk.CTkFrame):
    def __init__(self, parent, on_submit):
        super().__init__(parent)

        self.on_submit = on_submit

        self.saved_players = None
        if os.path.isfile('saved_players.json'):
            with open('saved_players.json', 'r') as f:
                self.saved_players: list[dict[str, str]] = json.load(f)

        self.user_entries = [ctk.CTkEntry(self, placeholder_text=f'Player {i+1}') for i in range(3)]
        for entry in self.user_entries:
            entry.pack(pady=10)

        self.save_players_button = ctk.CTkButton(self, text='Save Players', fg_color=GREEN, command=self.save_players)
        self.save_players_button.pack(pady=10)
        
        self.submit_users_button = ctk.CTkButton(self, text="Submit", command=self.submit_users)
        self.submit_users_button.pack(pady=10)

        self.saved_players_buttons = []
        if self.saved_players:
            for users_dict in self.saved_players:
                for key, value in users_dict.items():
                    button = ctk.CTkButton(self, text=key, fg_color=RED, command=lambda x=value: self.load_players(x))
                    button.pack(pady=10)

                    self.saved_players_buttons.append(button)
                    

    def load_players(self, usernames):
        print(usernames)

        for i, entry in enumerate(self.user_entries):
            entry.delete(0, "end")
            if i < len(usernames):
                entry.insert(0, usernames[i])


    def get_users(self):
        usernames = []

        for entry in self.user_entries:
            username = entry.get()

            if username:
                usernames.append(username)

        return usernames
    

    def save_players(self):
        usernames = self.get_users()

        if not usernames:
            return

        usernames_string = ', '.join(usernames)
        users_dict = {usernames_string:usernames}

        if self.saved_players:
            self.saved_players.append(users_dict)

            print('Appended to saved_players JSON')
        
        else:
            self.saved_players = [users_dict]
            
            print('Created saved_players JSON')

        with open('saved_players.json', "w") as f:
                json.dump(self.saved_players, f, indent=2)


    def submit_users(self):
        usernames = self.get_users()

        self.on_submit(usernames)




            



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.message_queue = queue.Queue()
        self.tracker = None
        
        self.title("RL Tracker")
        self.geometry("1000x800")

        ctk.set_default_color_theme('green')
        ctk.set_appearance_mode("dark")

        self.home_page = HomePage(self, self.start_tracking)
        self.tracking_page = None

        self.show_page(self.home_page)

    def show_page(self, page):
        # hide all pages then show the requested one
        for frame in (self.home_page, self.tracking_page):
            if frame:
                frame.pack_forget()
        # page.place(relx=0, rely=0, relwidth=1, relheight=1)
        page.pack(expand=True, fill='both')


    def start_tracking(self, usernames):
        self.tracker = RocketLeagueTracker(usernames, self.message_queue)

        thread = threading.Thread(target=self.tracker.connect, daemon=True)
        thread.start()

        self.tracking_page = TrackingPage(self, usernames, on_save=self.tracker.save)
        self.show_page(self.tracking_page)

        self.poll_queue()

    
    def poll_queue(self):
        while not self.message_queue.empty():
            self.message_queue.get()  # just draining the signal

            try:
                self.tracking_page.update(self.tracker.game_state, self.tracker.session_state)
            except Exception as e:
                print(f"GUI update error: {e}")

        self.after(100, self.poll_queue)


if __name__ == "__main__":
    app = App()
    app.mainloop()