from tracker import GameState

from gui.frames.utility_frames import StatRow, CustomFrame
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


class CurrentGamePlayerFrame(CustomFrame):
    def __init__(self, parent, usernames: list[str]):
        super().__init__(parent, title='This Game', additional_columns=['goals', 'assists', 'saves', 'shots', 'demos'])

        # FrameHeader(self, 'This game', additional_columns=['goals', 'assists', 'saves', 'shots', 'demos']).auto_pack()

        self.player_rows: dict[str, StatRow] = {}
        for username in usernames:
            row = StatRow(self, username, columns=[('int', 0),('int', 0),('int', 0),('int', 0),('int', 0)])
            row.pack(fill="x", padx=12, pady=2)
            self.player_rows[username] = row


    def update(self, game_state: GameState):
        for player in game_state.players:
            if player.username in self.player_rows:
                player_row = self.player_rows.get(player.username)

                player_row.update(player.goals, player.assists, player.saves, player.shots, player.demos)