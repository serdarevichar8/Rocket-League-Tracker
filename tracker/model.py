import os
import json
import pickle

from sklearn.ensemble import RandomForestClassifier

from tracker.game_state import GameState


MODEL_FILENAME = 'random_forest_model.pkl'
FEATURES = [
    'team_goals',
    'team_assists',
    'team_saves',
    'team_shots',
    'team_demos',
    'opp_goals',
    'opp_assists',
    'opp_saves',
    'opp_shots',
    'opp_demos',
    'seconds_remaining'
]


def connect_model() -> tuple[RandomForestClassifier | None, bool]:
    model_conn = None
    model_active = False

    if os.path.isfile(MODEL_FILENAME):
        with open(MODEL_FILENAME, 'rb') as f:
            model = pickle.load(f)

            if isinstance(model, RandomForestClassifier):
                model_conn = model
                model_active = True

                print('Model loaded')

    return model_conn, model_active


def run_model(model: RandomForestClassifier, game_state: GameState) -> int:
    X = [
        game_state.team_goals,
        sum(player.assists for player in game_state.players),
        sum(player.saves for player in game_state.players),
        sum(player.shots for player in game_state.players),
        sum(player.demos for player in game_state.players),
        game_state.opp.goals,
        game_state.opp.assists,
        game_state.opp.saves,
        game_state.opp.shots,
        game_state.opp.demos,
        game_state.seconds_remaining
    ]

    win_prob = model.predict_proba([X])[0][1]
    win_prob = int(win_prob * 100)

    return win_prob


def train_model(usernames: list[str]) -> None:
    '''
    Trains the model on all available events exports. Loops through all JSONs living
    in the `events_exports` directory for data. Performs the following steps:

    1) Loads data from `events_exports`
    2) Creates game snapshots, exporting the state of the game every 10 seconds
    3) Splits all games into train/test split (80/20)
    4) Trains Random Forest Classifier
    5) Tests model
    6) Saves to `random_forest_model.pkl`
    '''
    if not os.path.isdir('events_exports'):
        return

    # Load in events JSONs
    events_jsons = [f'events_exports/{file}' for file in os.listdir('events_exports') if file.startswith('events-export-') and file.endswith('.json')]

    events = []
    for filename in events_jsons:
        with open(filename, 'r') as f:
            data: dict[str, list] = json.load(f)

            loaded_usernames = data.get('usernames')
            if not loaded_usernames:
                continue
            if set(loaded_usernames) != set(usernames):
                continue

            events_data = data.get('events')
            events += events_data

    print(f'Total Events: {len(events)}\n')


    # Loop through events, saving the game state at every 10 second increment
    # On match end, save result and guid to a dictionary
    # Create dataframe and map result to match based on guid
    game_state = GameState(usernames)
    games: list[dict[str]] = []
    game_results: dict[str, int] = {}

    for event in events:
        game_state.handle_event(event)

        match_guid = event.get('Data').get('MatchGuid')

        if (game_state.seconds_remaining % 10 == 0) and (game_state.seconds_remaining != 300):

            game_data = {
                'team_goals':game_state.team_goals,
                'team_assists':sum(player.assists for player in game_state.players),
                'team_saves':sum(player.saves for player in game_state.players),
                'team_shots':sum(player.shots for player in game_state.players),
                'team_demos':sum(player.demos for player in game_state.players),
                'opp_goals':game_state.opp.goals,
                'opp_assists':game_state.opp.assists,
                'opp_saves':game_state.opp.saves,
                'opp_shots':game_state.opp.shots,
                'opp_demos':game_state.opp.demos,
                'seconds_remaining':game_state.seconds_remaining,
                'match_guid':match_guid
            }
            
            games.append(game_data)

        if event.get('Event') == 'MatchEnded':
            game_results[match_guid] = game_state.win

    for game in games:
        game['win'] = game_results.get(game.get('match_guid'))


    


    # Manual train/test split by match guid

    # Old approach:
    # Calculates what 20% of the total number of games are
    # Randomly samples the ids to build the 20% test list. Constructs Train list on the rest

    # New approach: select 1 out of every 5 games to test on
    match_guids = list(game_results.keys())
    # test_size = len(match_guids) // 5

    test_guids = [guid for index, guid in enumerate(match_guids) if index % 5 == 4]
    # test_guids = random.sample(match_guids, k=test_size)
    train_guids = [guid for guid in match_guids if guid not in test_guids]

    print(f'Total Games: {len(match_guids)}')
    print(f'Test Games: {len(test_guids)}')
    print(f'Train Games: {len(train_guids)}\n')

    test_snapshots = [game_snapshot for game_snapshot in games if game_snapshot.get('match_guid') in test_guids]
    train_snapshots = [game_snapshot for game_snapshot in games if game_snapshot.get('match_guid') in train_guids]

    print(f'Test Snapshots Length: {len(test_snapshots)}')
    print(f'Train Snapshots Length: {len(train_snapshots)}\n')


    # Creation of X and y test/train arrays
    # Convert to numpy arrays to avoid column label warnings when predicting with model
    X_train = [[game_snapshot[feature] for feature in FEATURES] for game_snapshot in train_snapshots]
    X_test = [[game_snapshot[feature] for feature in FEATURES] for game_snapshot in test_snapshots]

    y_train = [game_snapshot['win'] for game_snapshot in train_snapshots]
    y_test = [game_snapshot['win'] for game_snapshot in test_snapshots]


    # Train the model
    model = RandomForestClassifier(
                n_estimators=100,
                random_state=8,
                min_samples_leaf=30
            ).fit(X_train, y_train)


    # Test and evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f'Accuracy: {accuracy}\n')


    # Save the model
    with open('random_forest_model.pkl', 'wb') as f:
        pickle.dump(model, f)

        print('Model saved')



if __name__ == '__main__':
    usernames = []

    num_users = input('Enter number of users: ')
    num_users = int(num_users)

    if num_users < 1 or num_users > 3:
        raise ValueError(f'Number of users must be between 1 and 3, option entered was: {num_users}')

    for i in range(num_users):
        username = input(f'Username {i+1}: ')
        usernames.append(username)

    train_model(usernames)