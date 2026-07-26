import tkinter as tk

import customtkinter as ctk

from tracker import SessionState

from gui.frames.config import CARD_COLOR, LIGHT_GREY, BLUE, ORANGE, YELLOW
from gui.frames.utility_frames import CustomFrame


class PlayerChartFrame(CustomFrame):
    def __init__(self, parent):
        super().__init__(parent, 'Player Comparison')

        # FrameHeader(self, 'Player Comparison').auto_pack()

        self.height = 200
        self.width = 280
        self.top_pad = 5
        self.bot_pad = 5
        self.left_pad = 50
        self.right_pad = 5
        self.bar_pad = 5

        self.bar_coords: dict[str, tuple] = {}

        self.bar_chart = tk.Canvas(self, bg=CARD_COLOR, height=self.height, width=self.width, highlightthickness=0, borderwidth=0)
        self.bar_chart.pack(padx=5, pady=5)

        self.setup_chart()


    def setup_chart(self):
        chart_boundary = (self.height - self.top_pad - self.bot_pad)
        bar_area_height = chart_boundary / 5
        self.bar_pad

        for index, bar_name in enumerate(['goals', 'assists', 'saves', 'shots', 'demos']):
            x_0 = self.left_pad
            y_0 = self.top_pad + (index * bar_area_height) + self.bar_pad
            x_1 = self.width - self.right_pad
            y_1 = self.top_pad + ((index+1) * bar_area_height) - self.bar_pad
            y_2 = ((y_1 - y_0) / 2) + y_0

            self.bar_chart.create_text(
                0,
                y_2,
                text=bar_name.capitalize(),
                # justify='left',
                anchor='w',
                fill='gray'
            )

            self.bar_chart.create_rectangle(
                x_0,
                y_0,
                x_1,
                y_1,
                outline=LIGHT_GREY,
                tags=f'{bar_name}_bar'
            )

            self.bar_coords[f'{bar_name}_bar'] = (x_0, y_0, x_1, y_1, y_2)

    
    def update(self, session_state: SessionState):
        players = [player for username, player in session_state.players.items()]
        fill_colors = [BLUE, ORANGE, YELLOW]

        for stat in ['goals', 'assists', 'saves', 'shots', 'demos']:
            total_stat = sum(getattr(player, stat) for player in players)

            if total_stat > 0:
                self.bar_chart.delete(f'{stat}_bar')

                offset = 0
                for player, fill_color in zip(players, fill_colors):
                    x_0, y_0, x_1, y_1, y_2 = self.bar_coords.get(f'{stat}_bar')

                    player_pct = getattr(player, stat) / total_stat

                    player_bar_width = (self.width - self.left_pad - self.right_pad) * player_pct

                    self.bar_chart.create_rectangle(
                        self.left_pad + offset,
                        y_0,
                        self.left_pad + offset + player_bar_width,
                        y_1,
                        outline=LIGHT_GREY,
                        fill=fill_color,
                        tags=f'{stat}_bar'
                    )

                    if player_bar_width > 0:
                        self.bar_chart.create_text(
                            self.left_pad + offset + (player_bar_width / 2),
                            y_2,
                            text=player.username,
                            fill='black',
                            tags=f'{stat}_bar',
                            font=('default', 8)
                        )

                    offset += player_bar_width