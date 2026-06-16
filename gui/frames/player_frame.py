from tracker import PlayerStats, SessionState

from gui.frames.utility_frames import StatRow
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


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
