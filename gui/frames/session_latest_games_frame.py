from tracker import SessionState

from gui.frames.utility_frames import Square, FrameHeader
from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT

import customtkinter as ctk


class SessionLatestGamesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        FrameHeader(self, 'Last 10 Games').auto_pack()

        squares_row = ctk.CTkFrame(self, fg_color="transparent")
        squares_row.pack(pady=(10, 4))

        self.squares = [Square(squares_row, 1) for _ in range(10)]
        for index, square in enumerate(self.squares):
            square.grid(row=0, column=index, padx=5, pady=(0, 4))


    def update(self, session_state: SessionState):
        results = session_state.games[-10:][::-1]

        for index, result in enumerate(results):
            self.squares[index].update(result)