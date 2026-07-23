import tkinter as tk

import customtkinter as ctk

from tracker import GameState

from gui.frames.config import CARD_COLOR, CARD_HEADING_FONT, RED


AXES_LABEL_FONT = ('default', 10)
LIGHT_GREY = 'gray40'
LINE_COLOR = RED


class WinProbFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CARD_COLOR)

        ctk.CTkLabel(self, text="Win Probability", font=CARD_HEADING_FONT).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=(0, 4))

        self.height = 150
        self.width = 320
        # self.pad = 20
        self.top_pad = 10
        self.bot_pad = 20
        self.left_pad = 20
        self.right_pad = 10

        self.win_prob_canvas = tk.Canvas(self, bg=CARD_COLOR, height=self.height, width=self.width, highlightthickness=0, borderwidth=0)
        self.win_prob_canvas.pack(padx=5, pady=5)

        
        # Create outer axes
        self.win_prob_canvas.create_rectangle(self.left_pad, self.top_pad, self.width - self.right_pad, self.height - self.bot_pad, outline=LIGHT_GREY)

        # Calculate the midpoint of each axis
        mid_line_x, mid_line_y = self.convert_coords(150, 50)

        # Create median line at y = 50
        self.win_prob_canvas.create_line(self.left_pad, mid_line_y, self.width - self.right_pad, mid_line_y, fill=LIGHT_GREY)

        # Create x-ticks
        for x_tick in [300, 225, 150, 75, 0]:
            x, y = self.convert_coords(x_tick, 0)

            self.win_prob_canvas.create_text(x, self.height - (self.bot_pad / 2), text=str(x_tick), font=AXES_LABEL_FONT)

        # Create y-ticks
        for y_tick in [0, 25, 50, 75, 100]:
            x, y = self.convert_coords(0, y_tick)

            self.win_prob_canvas.create_text(self.left_pad / 2, y, text=str(y_tick), font=AXES_LABEL_FONT)


    def convert_coords(self, x, y):
        x_pct = (300 - x) / 300
        y_pct = y / 100

        x_coord = x_pct * (self.width - (self.left_pad + self.right_pad)) + self.left_pad
        y_coord = (1 - y_pct) * (self.height - (self.top_pad + self.bot_pad)) + self.top_pad

        return x_coord, y_coord
    

    def update(self, game_state: GameState):
        data = game_state.win_probabilities

        if len(data) >= 2:
            self.win_prob_canvas.delete('win_prob_line')

            for i in range(len(data) - 1):
                curr_point = data[i]
                next_point = data[i + 1]

                curr_coords = self.convert_coords(curr_point[0], curr_point[1])
                next_coords = self.convert_coords(next_point[0], next_point[1])

                self.win_prob_canvas.create_line(curr_coords[0], curr_coords[1], next_coords[0], next_coords[1], fill=LINE_COLOR, tags='win_prob_line')