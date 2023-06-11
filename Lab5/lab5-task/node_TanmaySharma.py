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
        len_ring = len(RING)

        # successor node
        for i in range(len_ring):
            if RING[i] == node_id:
                self.successor_id = RING[i % len_ring]
               

        # finger table
        for i in range(M):
            result = (node_id + 2**i) % 2**M
            node_index = -1
            for j in range(len_ring):
                if result > RING[j]:
                    continue
                node_index = j
                break
            if node_index != -1:
                self.finger_table.append(RING[node_index])
                continue
            else:
                node_index = 0
                self.finger_table.append(RING[node_index])

        print(f"Node created! Finger table = {self.finger_table}")

    def closest_preceding_node(self, id):
        """Returns node_id of the closest preceeding node (from n.finger_table) for a given id"""
        for i in reversed(range(0, M)):
            if self.finger_table[i] in range(self.node_id + 1, id):
                return self.finger_table[i]
        return self.node_id

    def find_successor(self, id):
        """Recursive function returning the identifier of the node responsible for a given id"""
        if id == self.node_id:
            return id

        if id in range(self.node_id + 1, self.successor_id + 1):
            return self.successor_id

        closest_node = self.closest_preceding_node(id)
        closest_node_proxy = ServerProxy(f'http://node_{closest_node}:{PORT}')
        print(f"Forwarding request (key={id}) to node {closest_node}")
        return closest_node_proxy.find_successor(id)

    def put(self, key, value):
        """Stores the given key-value pair in the node responsible for it"""
        print(f"put({key}, {value})")
        node_id = self.find_successor(key)

        # If the current node is responsible for the key, store it in its data store
        if node_id == self.node_id:
            self.store_item(key, value)
            return True
        else:
            # Otherwise, forward the put request to the responsible node
            with ServerProxy(f'http://node_{node_id}:{PORT}') as node:
                if node.store_item(key, value):
                    return True
                else:
                    return False

    def get(self, key):
        """Gets the value for a given key from the node responsible for it"""
        print(f"get({key})")
        node_id = self.find_successor(key)
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
    parser = ArgumentParser(description='Node id')
    parser.add_argument('node_id', type=int)
    args = parser.parse_args()

    node_id = args.node_id

    node = Node(node_id)

    with SimpleXMLRPCServer((f'0.0.0.0', PORT), logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(node)
        try:
            print(f"Server started at localhost:{PORT} for the node:{node_id}")
            server.serve_forever()
        except KeyboardInterrupt:
            print("Server is shutting down!")
