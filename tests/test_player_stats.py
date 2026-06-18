import json
import unittest

from tracker import PlayerStats


class TestPlayerStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''
        Load in specific test events to get one of each event type.
        '''
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
        '''
        Create 2 `PlayerStats` instances with different usernames.
        '''
        self.player = PlayerStats('test')
        self.player_2 = PlayerStats('test_2')


    def test_handle_goal(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a goal event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_goal)
        self.player_2.handle_event(self.event_goal)

        self.assertEqual(self.player.goals, 1)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)

        self.assertEqual(self.player_2.goals, 0)


    def test_handle_assist(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a assist event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_assist)
        self.player_2.handle_event(self.event_assist)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 1)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)

        self.assertEqual(self.player_2.assists, 0)


    def test_handle_save(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a save event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_save)
        self.player_2.handle_event(self.event_save)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 1)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)

        self.assertEqual(self.player_2.saves, 0)


    def test_handle_epic_save(self):
        '''
        Test the `handle_event` method of `PlayerStats` on an epic save event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_epic_save)
        self.player_2.handle_event(self.event_epic_save)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 1)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)

        self.assertEqual(self.player_2.saves, 0)


    def test_handle_shot(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a shot event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_shot)
        self.player_2.handle_event(self.event_shot)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 1)
        self.assertEqual(self.player.demos, 0)

        self.assertEqual(self.player_2.shots, 0)


    def test_handle_demo(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a demo event. Two `PlayerStats`
        instances are being tested. One is tested so that only the appropriate attribute
        was affected. The other is tested to make sure it was left unaffected since it's
        `username != mainTarget.name`
        '''
        self.player.handle_event(self.event_demo)
        self.player_2.handle_event(self.event_demo)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 1)

        self.assertEqual(self.player_2.demos, 0)


    def test_handle_clock(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a clockUpdated event.
        The instance is tested to ensure no attributes were affected.
        '''
        self.player.handle_event(self.event_clock)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)


    def test_handle_start(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a matchInitialized event.
        The instance is tested to ensure no attributes were affected.
        '''
        self.player.handle_event(self.event_start)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)


    def test_handle_end(self):
        '''
        Test the `handle_event` method of `PlayerStats` on a matchEnded event.
        The instance is tested to ensure no attributes were affected.
        '''
        self.player.handle_event(self.event_end)

        self.assertEqual(self.player.goals, 0)
        self.assertEqual(self.player.assists, 0)
        self.assertEqual(self.player.saves, 0)
        self.assertEqual(self.player.shots, 0)
        self.assertEqual(self.player.demos, 0)


    def test_reset(self):
        '''
        Test the `reset` method of `PlayerStats` by checking whether the entire object's
        dict is the same as a freshly created one.
        '''
        self.player.goals = 1
        self.player.assists = 1
        self.player.saves = 1
        self.player.shots = 1
        self.player.demos = 1

        self.player.reset()

        fresh_player = PlayerStats('test')

        self.assertEqual(self.player.__dict__, fresh_player.__dict__)


    def test_export(self):
        '''
        Test the `export` method of `PlayerStats` by setting all its attributes
        to different values, then checking whether it matches the correct dictionary
        result.
        '''
        self.player.goals = 1
        self.player.assists = 2
        self.player.saves = 3
        self.player.shots = 4
        self.player.demos = 5

        data = self.player.export()

        correct_result = {
            'test_goals':1,
            'test_assists':2,
            'test_saves':3,
            'test_shots':4,
            'test_demos':5
        }

        self.assertEqual(data, correct_result)




if __name__ == '__main__':
    unittest.main()