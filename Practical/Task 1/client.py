import json
import socket

class Query:
    def __init__(self, type, key):
        self.type = type
        self.key = key

queries = [
    Query(type="A", key="example.com"),
    Query(type="PTR", key="1.2.3.4"),
    Query(type="CNAME", key="moodle.com"),
]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for query in queries:
    data = json.dumps({"type": query.type, "key": query.key}).encode()

    print(f"Client: Sending query for {query.key}")
    sock.sendto(data, ("localhost", 50000))

    data, _ = sock.recvfrom(20480)
    answer = json.loads(data.decode())

    print(f"Server: {answer}")

sock.close()
