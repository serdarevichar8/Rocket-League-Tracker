import os
import json

import customtkinter as ctk

from gui.frames.config import GREEN, RED


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, on_submit):
        super().__init__(parent)

        self.on_submit = on_submit

        self.saved_players = None
        if os.path.isfile('saved_players.json'):
            with open('saved_players.json', 'r') as f:
                self.saved_players: list[dict[str, str]] = json.load(f)

        self.user_entries = [ctk.CTkEntry(self, placeholder_text=f'Player {i+1}') for i in range(3)]
        for entry in self.user_entries:
            entry.pack(pady=10)

        self.save_players_button = ctk.CTkButton(self, text='Save Players', fg_color=GREEN, command=self.save_players)
        self.save_players_button.pack(pady=10)
        
        self.submit_users_button = ctk.CTkButton(self, text="Submit", command=self.submit_users)
        self.submit_users_button.pack(pady=10)

        self.saved_players_buttons = []
        if self.saved_players:
            for users_dict in self.saved_players:
                for key, value in users_dict.items():
                    button = ctk.CTkButton(self, text=key, fg_color=RED, command=lambda x=value: self.load_players(x))
                    button.pack(pady=10)

                    self.saved_players_buttons.append(button)
                    

    def load_players(self, usernames):
        print(usernames)

        for i, entry in enumerate(self.user_entries):
            entry.delete(0, "end")
            if i < len(usernames):
                entry.insert(0, usernames[i])


    def get_users(self):
        usernames = []

        for entry in self.user_entries:
            username = entry.get()

            if username:
                usernames.append(username)

        return usernames
    

    def save_players(self):
        usernames = self.get_users()

        if not usernames:
            return

        usernames_string = ', '.join(usernames)
        users_dict = {usernames_string:usernames}

        if self.saved_players:
            self.saved_players.append(users_dict)

            print('Appended to saved_players JSON')
        
        else:
            self.saved_players = [users_dict]
            
            print('Created saved_players JSON')

        with open('saved_players.json', "w") as f:
                json.dump(self.saved_players, f, indent=2)


    def submit_users(self):
        usernames = self.get_users()

        self.on_submit(usernames)
