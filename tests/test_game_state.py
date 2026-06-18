import unittest
from datetime import datetime

from tracker import PlayerStats, GameState


class TestGameState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        return

        with open('tests/test_events.json', 'r') as f:
            cls.events: list[dict] = json.load(f)

        cls.event_goal = cls.events[1]
        cls.event_assist = cls.events[2]
        cls.event_shot = cls.events[0]
        cls.event_epic_save = cls.events[4]
        cls.event_demo = cls.events[5]
        cls.event_clock = cls.events[3]
        cls.event_start = cls.events[6]
        cls.event_end = cls.events[7]
        cls.event_save = cls.events[8]


    def setUp(self):
        self.game_state = GameState(['test'])


    def test_initialization(self):
        '''
        Test the `__init__` method of `GameState` on the following:
        - If the players list argument is building the correct number of `PlayerStats` instances
        - If the `opp` attribute is being built as a `PlayerStats` instance
        '''
        self.assertEqual(len(self.game_state.players), 1)

        test_game_state = GameState(['test','test_2'])
        self.assertEqual(len(test_game_state.players), 2)

        self.assertIsInstance(self.game_state.opp, PlayerStats)


    def test_reset(self):
        '''
        Test the `reset` method of `GameState` by checking whether the entire object's
        dict is the same as a freshly created one.
        '''
        self.game_state.team_goals = 3
        self.game_state.lead = 1
        self.game_state.overtime = 1
        self.game_state.win = 1
        self.game_state.margin = 2

        self.game_state.reset()

        fresh_game = GameState(['test'])

        self.assertEqual(self.game_state.__dict__, fresh_game.__dict__)


    def test_export(self):
        pass


    def test_handle_event(self):
        pass