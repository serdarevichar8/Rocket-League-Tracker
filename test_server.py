import time
import socket
import json

with open('test_events.json', 'r') as f:
    events: list[dict] = json.load(f)

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

            for event in events:
                try:
                    event_bytes = json.dumps(event).encode()
                    conn.send(event_bytes)
                    time.sleep(0.25)

                except Exception as e:
                    print(f'Client disconected mid-loop, error: {e}')
                    break

            # conn.close()
            # print(f'Closed connection to: {address[0]}:{address[1]}')



except Exception as e:
    print(f'Failed to bind, error: {e}')