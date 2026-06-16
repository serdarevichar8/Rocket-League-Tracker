from gui.frames.config import GREEN, RED, CARD_COLOR

import customtkinter as ctk


class StatRow(ctk.CTkFrame):
    def __init__(self, parent, label: str, columns: list[tuple] = [('int', 0)]):
        super().__init__(parent, fg_color="transparent")

        self.columnconfigure(0, weight=1)  # label takes remaining space

        self.label = ctk.CTkLabel(self, text=label, text_color="gray")
        self.label.grid(row=0, column=0, sticky="w")

        self.value_labels: list[ctk.CTkLabel] = []
        for index, column_tuple in enumerate(columns):
            data_type, initial_value = column_tuple

            value_label = ctk.CTkLabel(self, text='', anchor='center', width=40)
            value_label.grid(row=0, column=(index + 1), padx=(0, 0), sticky="e")

            self.value_labels.append((value_label, data_type))

        initial_values = [initial_value for data_type, initial_value in columns]
        self.update(*initial_values)


    def update(self, *args):
        '''
        Updates the values in the statrow, leaves the label the same.

        Takes any number of positional arguments, will take them in the same order as the value labels.

        Make sure to only enter the same number of arguments as values in the statrow.
        '''
        if len(self.value_labels) != len(args):
            raise ValueError('The number of arguments must be equal to the number of values added to the statrow')

        for index, value in enumerate(args):
            value_label, data_type = self.value_labels[index]
            value_label: ctk.CTkLabel

            if data_type == 'int':
                if not isinstance(value, int):
                    raise ValueError(f'Stat row value must be an int, value passed was {value}')
                
                value_label.configure(text=str(value))

            elif data_type == 'float':
                if not isinstance(value, float):
                    raise ValueError(f'Stat row value must be a float, value passed was {value}')
                
                value_label.configure(text=str(round(value, 1)))

            elif data_type == 'bool':
                if value not in (0, 1):
                    raise ValueError(f'Stat row value must be either 0 or 1, value passed was {value}')
                
                bool_text = 'Yes' if value else 'No'
                bool_color = GREEN if value else RED

                value_label.configure(text=bool_text, text_color=bool_color)

            elif data_type == 'pct':
                if not isinstance(value, int):
                    raise ValueError(f'Stat row value must be an int, value passed was {value}')
                
                value_label.configure(text=f'{value}%')


class MiniCard(ctk.CTkFrame):
    def __init__(self, parent, label: str, value, color = 'white'):
        super().__init__(parent, fg_color=CARD_COLOR)

        self.label = label
        self.value = value

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(4, 0))

        ctk.CTkLabel(header_row, text=self.label, text_color='gray').grid(row=0, column=0, sticky='w')

        self.value_label = ctk.CTkLabel(self, text=self.value, text_color=color, font=("default", 36, 'bold'))
        self.value_label.pack(padx=16, pady=(0, 4), side='left')

    
    def update(self, value, color = None):
        self.value = value
        self.value_label.configure(text=str(self.value))
        if color:
            self.value_label.configure(text_color=color)


class Square(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent, fg_color='transparent', border_color='gray30', border_width=1, height=20, width=20)


    def update(self, result = None):
        if isinstance(result, dict):
            result = result.get('win')

        if result == 1:
            self.configure(fg_color=GREEN)
        elif result == 0:
            self.configure(fg_color=RED)
