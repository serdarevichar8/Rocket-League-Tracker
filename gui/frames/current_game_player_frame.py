from tracker import GameState

from gui.frames.utility_frames import StatRow, FrameHeader
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


class CurrentGamePlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, usernames: list[str]):
        super().__init__(parent, fg_color=CARD_COLOR)

        FrameHeader(self, 'This game', additional_columns=['goals', 'saves', 'demos']).auto_pack()

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