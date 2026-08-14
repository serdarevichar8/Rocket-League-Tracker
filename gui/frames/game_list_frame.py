import customtkinter as ctk

from gui.frames.config import CARD_COLOR

class GameListFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, height=50, fg_color=CARD_COLOR)