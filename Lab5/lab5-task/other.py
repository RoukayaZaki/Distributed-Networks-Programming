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
        self.predecessor = RING[(RING.index(node_id) - 1) % len(RING)]        
        self.successor = RING[(RING.index(node_id) + 1) % len(RING)]
        self.data_store = {}
        for i in range(M):
            self.finger_table.append(self.ft_successor((node_id + 2**i) % 2**M))
        print(f"Node created! Finger table = {self.finger_table}")

    def ft_successor(self, id):
        return next((node for node in RING if node >= id), RING[0])

    def in_interval(self, id, L, R):
        # L <= R does not necessarily hold
        if L <= id <= R: 
            return True
        if L >= R and (id >= L or id <= R):
            return True
        return False

    def closest_preceding_node(self, id):
        """Returns node_id of the closest preceeding node (from n.finger_table) for a given id"""
        for i in range(M - 1, -1, -1):
            if self.in_interval(self.finger_table[i], self.node_id + 1, id - 1): # (n.id, id)
                return self.finger_table[i]
        return self.node_id

    def find_successor(self, id):
        """Recursive function returning the identifier of the node responsible for a given id"""
        if self.in_interval(id, self.predecessor + 1, self.node_id): # (predecessor_id, n.id]
            return self.node_id

        if self.in_interval(id, self.node_id + 1, self.successor): # (n.id, n.successor_id]
            return self.successor

        n0 = self.closest_preceding_node(id)
        n0_proxy = ServerProxy(f'http://node_{n0}:{PORT}')
        print(f"Forwarding request (key={id}) to node {n0}")
        return n0_proxy.find_successor(id)

    def put(self, key, value):
        """Stores the given key-value pair in the node responsible for it"""
        if key < 0 or key >= 2**M:
            return False
        print(f"put({key}, {value})")
        successor = self.find_successor(key)
        if successor == self.node_id: # if the current node contains the key 
            return self.store_item(key, value)
        else:
            successor_proxy = ServerProxy(f'http://node_{successor}:{PORT}')
            return successor_proxy.store_item(key, value)

    def get(self, key):
        """Gets the value for a given key from the node responsible for it"""
        print(f"get({key})")
        successor = self.find_successor(key)
        if successor == self.node_id: 
            return self.retrieve_item(key)
        else:
            successor_proxy = ServerProxy(f'http://node_{successor}:{PORT}')
            return successor_proxy.retrieve_item(key)

    def store_item(self, key, value):
        """Stores a key-value pair into the data store of this node"""
        self.data_store[key] = value
        return True

    def retrieve_item(self, key):
        """Retrieves a value for a given key from the data store of this node"""
        if key in self.data_store:
            return self.data_store[key]
        else:
            return -1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('node_id', type = int)
    args = parser.parse_args()

    node = Node(args.node_id)
    server = SimpleXMLRPCServer((f"node_{args.node_id}", PORT), logRequests = False)
    server.register_instance(node)
    server.serve_forever()