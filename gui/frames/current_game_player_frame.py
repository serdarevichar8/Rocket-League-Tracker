from tracker import GameState

from gui.frames.utility_frames import StatRow
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


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