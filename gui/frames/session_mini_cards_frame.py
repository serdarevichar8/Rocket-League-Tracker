from tracker import SessionState

from gui.frames.utility_frames import MiniCard
from gui.frames.config import GREEN, RED

import customtkinter as ctk


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