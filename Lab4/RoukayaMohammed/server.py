import sqlite3
from concurrent.futures import ThreadPoolExecutor

import grpc
import schema_pb2 as stub
import schema_pb2_grpc as service

SERVER_ADDR = '0.0.0.0:1234'


class Database(service.DatabaseServicer):
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def PutUser(self, request, context):
        print(f'PutUser({request.user_id}, {request.user_name})')
        try:

            conn = sqlite3.connect('db.sqlite')
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM Users WHERE user_id=?', (request.user_id,))
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute('INSERT INTO Users (user_id, user_name) VALUES (?, ?)', (request.user_id, request.user_name))
            else:
                cur.execute('UPDATE Users SET user_name=? WHERE user_id=?', (request.user_name, request.user_id))
            conn.commit()
            conn.close()
            return stub.ReturnMessage(status=True)
        
        except Exception as e:
            print('Error in PutUser:', e)
            return stub.ReturnMessage(status=False)

    def GetUsers(self, request, context):
        print(f'GetUsers()')
        try:

            conn = sqlite3.connect('db.sqlite')
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users")
            rows = cur.fetchall()
            conn.commit()
            conn.close()
            users = []
            for row in rows:
                user = stub.User(user_id=row[0], user_name=row[1])
                users.append(user)
            return stub.UsersList(users=users)
        
        except Exception as e:
            print('Error in GetUsers:', e)
            return stub.UsersList(users=[])

    def DeleteUser(self, request, context):

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('DELETE FROM Users WHERE user_id=?', (request.user_id,))
        deleted_rows = cur.rowcount
        conn.commit()
        conn.close()
        if deleted_rows > 0:
            return stub.ReturnMessage(status=True)
        else:
            return stub.ReturnMessage(status=False)


if __name__ == '__main__':

    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Users (user_id INTEGER PRIMARY KEY, user_name VARCHAR(50) NOT NULL)')
    conn.commit()
    conn.close()

    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    print('Listening on 0.0.0.0:1234')
    service.add_DatabaseServicer_to_server(Database(), server)
    server.add_insecure_port(SERVER_ADDR)
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        print("Shutting down...")

# Note:
# I used ChatGPT to help with sqlite3 commands.