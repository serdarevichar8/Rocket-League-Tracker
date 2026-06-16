import threading
import queue

import customtkinter as ctk

from tracker import RocketLeagueTracker
from gui.home_page import HomePage
from gui.tracking_page import TrackingPage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.message_queue = queue.Queue()
        self.tracker = None
        
        self.title("RL Tracker")
        self.geometry("1000x800")

        ctk.set_default_color_theme('green')
        ctk.set_appearance_mode("dark")

        self.home_page = HomePage(self, self.start_tracking)
        self.tracking_page = None

        self.show_page(self.home_page)


    def show_page(self, page):
        # hide all pages then show the requested one
        for frame in (self.home_page, self.tracking_page):
            if frame:
                frame.pack_forget()
        # page.place(relx=0, rely=0, relwidth=1, relheight=1)
        page.pack(expand=True, fill='both')


    def start_tracking(self, usernames):
        self.tracker = RocketLeagueTracker(usernames, self.message_queue)

        thread = threading.Thread(target=self.tracker.connect, daemon=True)
        thread.start()

        self.tracking_page = TrackingPage(self, usernames, on_save=self.tracker.save)
        self.show_page(self.tracking_page)

        self.poll_queue()

    
    def poll_queue(self):
        while not self.message_queue.empty():
            self.message_queue.get()  # just draining the signal

            try:
                self.tracking_page.update(self.tracker.game_state, self.tracker.session_state)
            except Exception as e:
                print(f"GUI update error: {e}")

        self.after(100, self.poll_queue)