import json
import socket

class RR:
    def __init__(self, type, key, value):
        self.type = type
        self.key = key
        self.value = value

records = [
    RR(type="A", key="example.com", value="1.2.3.4"),
    RR(type="PTR", key="1.2.3.4", value="example.com"),
]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 50000))
print("Server: listening on 0.0.0.0:50000")

try:
    while True:

        data, address = sock.recvfrom(20480)
        query = json.loads(data.decode())
        print(f"Client: {query}")
        for rr in records:
            if rr.type == query["type"] and rr.key == query["key"]:
                answer = {"type": rr.type, "key": rr.key, "value": rr.value}
                sock.sendto(json.dumps(answer).encode(), address)
                print("Server: Record found. Sending answer.")
                break
        else:
            error = {"type": query["type"], "key": query["key"], "value": "NXDOMAIN"}
            sock.sendto(json.dumps(error).encode(), address)
            print("Server: Record not found. Sending error.")

except KeyboardInterrupt:
    print("Server: Shutting down...")
finally:
    sock.close()
