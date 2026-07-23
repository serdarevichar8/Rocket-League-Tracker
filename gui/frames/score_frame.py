from tracker import GameState

from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT
from gui.frames.utility_frames import FrameHeader

import customtkinter as ctk


class ScoreFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        FrameHeader(self, 'Score').auto_pack()

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