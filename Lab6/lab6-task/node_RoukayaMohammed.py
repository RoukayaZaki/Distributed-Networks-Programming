import random
import sched
import socket
import time
from threading import Thread
from argparse import ArgumentParser
from enum import Enum
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

PORT = 1234
CLUSTER = [1, 2, 3]
ELECTION_TIMEOUT = (6, 8)
HEARTBEAT_INTERVAL = 5


class NodeState(Enum):
    """Enumerates the three possible node states (follower, candidate, or leader)"""
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


class Node:
    def __init__(self, node_id):
        """Non-blocking procedure to initialize all node parameters and start the first election timer"""
        self.node_id = node_id
        self.state = NodeState.FOLLOWER
        self.term = 0
        self.votes = {}
        self.log = []
        self.pending_entry = ''
        self.sched = sched.scheduler()
        #start election timer for this node
        self.timeout = random.uniform(*ELECTION_TIMEOUT)
        self.event = self.sched.enter(delay=self.election_timeout, priority=0, action=self.hold_election)
        print(f"Node started! State: {self.state}. Term: {self.term}")

    def is_leader(self):
        """Returns True if this node is the elected cluster leader and False otherwise"""
        if self.state == NodeState.LEADER:
            return True
        return False

    def reset_election_timer(self):
        """Resets election timer for this (follower or candidate) node and returns it to the follower state"""
        self.sched.cancel(self.event)
        self.timeout = random.uniform(*ELECTION_TIMEOUT)
        self.event = self.sched.enter(delay=self.election_timeout, priority=1, action=self.hold_election)
        return

    def hold_election(self):
        """Called when this follower node is done waiting for a message from a leader (election timeout)
            The node increments term number, becomes a candidate and votes for itself.
            Then call request_vote over RPC for all other online nodes and collects their votes.
            If the node gets the majority of votes, it becomes a leader and starts the hearbeat timer
            If the node loses the election, it returns to the follower state and resets election timer.
        """
        self.term += 1
        self.state = NodeState.CANDIDATE
        self.votes[self.term].append(self.node_id)

        for node in CLUSTER:
            if node == self.node_id:
                continue

            try:
                with ServerProxy(f'http://node_{node}:{PORT}') as follower_node:
                    print(f"Requesting vote from {node}")
                    if follower_node.request_vote(self.term, self.node_id):
                        self.votes[self.term].append(node)
            except:
                print(f"Node {node} is offline")

        if len(self.votes[self.term]) > len(self.nodes) // 2:
            print(f"Received majority of votes.")
            self.state = NodeState.LEADER
            # TODO: find the appropriate action
            self.heartbeat()
        else:
            print(f"Received less than majority of votes.")
            self.state = NodeState.FOLLOWER
            self.reset_election_timer()

        print(f"New election term {self.term}. State: {self.state}")
        return

    def request_vote(self, term, candidate_id):
        """Called remotely when a node requests voting from other nodes.
            Updates the term number if the received one is greater than `self.term`
            A node rejects the vote request if it's a leader or it already voted in this term.
            Returns True and update `self.votes` if the vote is granted to the requester candidate and False otherwise.
        """

        self.term = max(term, self.term)
        print(f"Got a vote request from {candidate_id} (term={term})")

        if self.is_leader() or term in self.votes:
            return False
        
        self.votes[self.term].append(self.node_id)

        return True

    def append_entries(self):
        """Called by leader every HEARTBEAT_INTERVAL, sends a heartbeat message over RPC to all online followers.
            Accumulates ACKs from followers for a pending log entry (if any)
            If the majority of followers ACKed the entry, the entry is committed to the log and is no longer pending
        """
        print("Sending a heartbeat to followers")
         # If this node is not the leader, do nothing.
        if not self.is_leader():
            return
        
        # Send a heartbeat message over RPC to all online followers.
        acks = 0
        for node in CLUSTER:
            if node == self.node_id:
                continue
            try:
                proxy = ServerProxy(f'http://node_{node}:{PORT}')
                ack = proxy.heartbeat(self.pending_entry)
                
                # If a follower fails to respond, catch the exception and print an error message.
            except socket.error:
                print(f"Could not reach node {node}.")
            
            if ack:
                acks += 1
        
        # If the majority of followers ACKed the entry, commit it to the log and clear the pending entry.
        if acks > len(CLUSTER) // 2:
            self.log.append(self.pending_entry)
            self.pending_entry = ''
            print(f"Leader {self.node_id} committed entry '{self.log[-1]}' to the log.")
            return True
        
        return False

    def heartbeat(self, leader_entry):
        """Called remotely from the leader to inform followers that it's alive and supply any pending log entry
            Followers would commit an entry if it was pending before, but is no longer now.
            Returns True to ACK the heartbeat and False on any problems.
        """
        print(f"Heartbeat received from leader (entry='{leader_entry}')")

        self.reset_election_timer()



        return True

    def leader_receive_log(self, log):
        """Called remotely from the client. Executed only by the leader upon receiving a new log entry
            Returns True after the entry is committed to the leader log and False on any problems
        """
        print(f"Leader received log '{log}' from client")
        while True:
            if self.pending_entry == "":
                break

        self.pending_entry = log
        self.append_entries()

        return True


if __name__ == '__main__':
    # Parse one integer argument (node_id), then create the node with that ID.
    # TODO: Start RPC server on 0.0.0.0:PORT and expose the node instance
    # TODO: Run the node scheduler in an isolated thread.
    # TODO: Handle KeyboardInterrupt and terminate gracefully.
    parser = ArgumentParser()
    parser.add_argument("node_id", type=int)
    args = parser.parse_args()
    node_id = args.node_id
    node = Node(node_id)
