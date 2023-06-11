from argparse import ArgumentParser
from bisect import bisect_left
from threading import Thread
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

M = 5
PORT = 1234
RING = [2, 7, 11, 17, 22, 27]


class Node:
    def __init__(self, node_id):
        """Initializes the node properties and constructs the finger table according to the Chord formula"""
        self.finger_table = []
        self.node_id = node_id
        self.data_store = {}
        self.successor = None

        flag = True
        for i in range(M):
            successor = (node_id + 2 ** i) % 2 ** M
            for node in RING:
                if node >= successor:
                    self.finger_table.append(node)
                    flag = False
                    break
            if flag:
                self.finger_table.append(RING[0])
        
        # Successor function returns the identifier of the next online node in the ring (clockwise direction).
        flag = True
        for node in RING:
            if node > self.node_id:
                self.successor = node
                flag = False
                break
        if flag:
            self.successor = RING[0]
       
        print(f"Node created! Finger table = {self.finger_table}")

    def closest_preceding_node(self, id):
        for i in range(M-1, -1, -1):
            if self.node_id < self.finger_table[i] < id:
                return self.finger_table[i]
        return self.node_id

    def find_successor(self, id):
        """Recursive function returning the identifier of the node responsible for a given id"""
        if id == self.node_id:
            return id
        
        if self.node_id < id <= self.successor:
            print(f"Forwarding request (key={id}) to node {self.successor}")
            return self.successor
       
        n0 = self.closest_preceding_node(id)
        print(f"Forwarding request (key={id}) to node {n0}")
        with ServerProxy(f'http://node_{n0}:{PORT}') as node0:
            return node0.find_successor(id)

    def put(self, key, value):
        """Stores the given key-value pair in the node responsible for it"""
        print(f"put({key}, {value})")
        try:
            node_id = self.find_successor(key)
            if node_id == self.node_id:
                self.store_item(key, value)
                return True
            else:
                with ServerProxy(f'http://node_{node_id}:{PORT}') as node:
                    node.store_item(key, value)
                return True
        except:
            return False

    def get(self, key):
        """Gets the value for a given key from the node responsible for it"""
        print(f"get({key})")
        node_id = self.find_successor(key)

        # Retrieve the value from the node's data store
        with ServerProxy(f'http://node_{node_id}:{PORT}') as node:
            return node.retrieve_item(key)

    def store_item(self, key, value):
        """Stores a key-value pair into the data store of this node"""
        self.data_store[key] = value
        return True
    
    def retrieve_item(self, key):
        """Retrieves a value for a given key from the data store of this node"""
        return self.data_store.get(key, -1)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("node_id", type=int)
    args = parser.parse_args()
    node_id = args.node_id
    with SimpleXMLRPCServer(('0.0.0.0', PORT), logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Node(node_id))
        try:
            print(f"RPC server is listening at http://0.0.0.0:{PORT}")
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")

    
