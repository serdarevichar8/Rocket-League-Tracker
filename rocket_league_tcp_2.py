from tracker import RocketLeagueTracker

if __name__ == "__main__":
    tracker = RocketLeagueTracker(['tekjnbo','ilovethezoo46'])
    try:
        tracker.connect()
    except KeyboardInterrupt:
        tracker.save()
        print("Stopped by user")