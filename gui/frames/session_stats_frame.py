from tracker import SessionState

from gui.frames.utility_frames import StatRow
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


class SessionStatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))
        # header_row.columnconfigure(0, weight=1)

        ctk.CTkLabel(header_row, text="Session Stats", font=CARD_HEADING_FONT).grid(row=0, column=0, sticky="w")
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.win_rate = StatRow(self, "Win Rate", columns=[('pct', 0), ('pct', 51)])
        self.lead_conversion = StatRow(self, "Lead Conversion", columns=[('pct', 0), ('pct', 79)])
        self.ot_rate = StatRow(self, "OT Win Rate", columns=[('pct', 0), ('pct', 51)])
        self.game_length = StatRow(self, "Avg Game Length", columns=[('time', 0), ('time', 386)])
        self.avg_opp_goals = StatRow(self, 'Avg Opp G/g', columns=[('float', 0.0), ('float', 2.66)])
        self.goal_differential = StatRow(self, "Goal Differential", columns=[('int', 0)])
        self.save_rate = StatRow(self, 'Save Rate (saves / saves+goals)', columns=[('pct', 0), ('pct', 64)])
        self.shooting_accuracy = StatRow(self, 'Shooting Accuracy', columns=[('pct', 0), ('pct', 37)])
        self.assist_rate = StatRow(self, 'Assist Rate', columns=[('pct', 0), ('pct', 45)])
        self.demo_ratio = StatRow(self, 'Demo Ratio', columns=[('float', 0.0), ('float', 0.76)])

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

        self.win_rate.update(win_rate, 51)
        self.lead_conversion.update(lead_rate, 79)
        self.ot_rate.update(ot_rate, 51)
        self.game_length.update(session_state.avg_game_length, 386)
        self.avg_opp_goals.update(session_state.opp.goals / divisor, 2.66)
        self.goal_differential.update(goal_differential)
        self.save_rate.update(save_rate, 64)
        self.shooting_accuracy.update(shooting_accuracy, 37)
        self.assist_rate.update(assist_rate, 45)
        self.demo_ratio.update(demo_ratio, 0.76)
