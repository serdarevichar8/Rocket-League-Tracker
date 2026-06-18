import time
import socket
import json

with open('test_events.json', 'r') as f:
    events: list[dict] = json.load(f)

# print(len(events))
# event_byte = json.dumps(events[1]).encode()



HOST = "127.0.0.1"
PORT = 49123

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print('Binded to socket')

        s.listen(1)
        print('Listening...')

        while True:
            conn, address = s.accept()

            print(f'Connected to: {address[0]}:{address[1]}')

            for index, event in enumerate(events):
                try:
                    event_bytes = json.dumps(event).encode()
                    conn.send(event_bytes)

                    if (index % 5 == 0) or (index + 1 == len(events)):
                        progress = int((index+1) / len(events) * 100)

                        print(f"\rProgress {progress}%", end="", flush=True)

                    time.sleep(0.25)

                except Exception as e:
                    print(f'Client disconected mid-loop, error: {e}')
                    break

            print('\nDone sending test events')

            if not conn.recv(1):
                print(f'Client disconnected: {address[0]}:{address[1]}')



except Exception as e:
    print(f'Failed to bind, error: {e}')