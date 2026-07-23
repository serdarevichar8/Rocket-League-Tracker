from tracker import GameState

from gui.frames.utility_frames import StatRow
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


class GameStatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        ctk.CTkLabel(self, text="Game stats", font=CARD_HEADING_FONT).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.largest_lead = StatRow(self, "Largest lead", columns=[('int', 0)])
        self.largest_deficit = StatRow(self, "Largest deficit", columns=[('int', 0)])
        self.lead_flag = StatRow(self, "Lead at any point", columns=[('bool', 0)])
        self.ot_flag = StatRow(self, "Overtime", columns=[('bool', 0)])
        self.win_prob = StatRow(self, 'Win Probability', columns=[('pct', 50)])
        # self.max_win_prob = StatRow(self, 'Max Win Probability', columns=[('pct', 50)])
        # self.min_win_prob = StatRow(self, 'Min Win Probability', columns=[('pct', 50)])

        for row in (
            self.largest_lead,
            self.largest_deficit,
            self.lead_flag,
            self.ot_flag,
            self.win_prob,
            # self.max_win_prob,
            # self.min_win_prob
        ):
            row.pack(fill="x", padx=12, pady=2)

    def update(self, game_state: GameState):
        self.largest_lead.update(game_state.largest_lead)
        self.largest_deficit.update(game_state.largest_deficit)
        self.lead_flag.update(game_state.lead)
        self.ot_flag.update(game_state.overtime)
        self.win_prob.update(game_state.win_prob)
        # self.max_win_prob.update(game_state.max_win_prob)
        # self.min_win_prob.update(game_state.min_win_prob)