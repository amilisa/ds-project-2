import rpyc
import random
from multiprocessing import Process
from consts import PORT, NF, F, PRIMARY, SECONDARY, STATES, ATTACK, RETREAT, UNDEFINED
from rpc_service import RPCService
from rpyc.utils.server import ThreadedServer


class Node(Process):
    def __init__(self, port, generals_number):
        super().__init__()
        self.id = port % PORT + 1
        self.port = port
        self.ports = list(range(PORT, PORT + generals_number))
        self.ports.remove(self.port)
        self.primary_port = None
        self.state = NF
        self.majority = None
        self.order = None
        self.votes = {ATTACK: 0, RETREAT: 0}
        self.fauly_generals_number = 0
        self.generals_number = generals_number
        self.rpc_service = RPCService(self)

    def define_order(self, order):
        self.majority = order
        for port in self.ports:
            if self.state == F:
                self.set_order(random.choice(STATES))
            else:
                self.set_order(order)
            conn = rpyc.connect("localhost", port)
            conn.root.set_order(self.order)
            conn.close()

        for port in self.ports:
            conn = rpyc.connect("localhost", port)
            response = conn.root.perform_quorum()
            conn.close()
            if response != UNDEFINED:
                self.votes[response] += 1

        if self.generals_number < 3 * self.fauly_generals_number + 1:
            return f"Execute order: cannot be determined - not enough generals in the system! " + \
                f"{self.fauly_generals_number} faulty node in the system: " + \
                f"{self.generals_number - self.fauly_generals_number} out of {self.generals_number} quorum not consistent."
        else:
            order = max(self.votes, key=self.votes.get)
            return f"Execute order: {order}! " + \
                f"{'Non-faulty' if self.fauly_generals_number == 0 else self.fauly_generals_number + 'faulty'} nodes in the system: " + \
                f"{self.generals_number - 1 - self.fauly_generals_number} out of {self.generals_number} quorum suggest {order}."

    def set_order(self, order):
        self.order = order

    def perform_quorum(self):
        for port in self.ports:
            if port != self.primary_port:
                conn = rpyc.connect("localhost", port)
                order = conn.root.get_order()
                conn.close()
                self.votes[order] += 1

        if self.votes[ATTACK] == self.votes[RETREAT]:
            self.majority = UNDEFINED
        else:
            self.majority = max(self.votes, key=self.votes.get)
        return self.majority

    def get_order(self):
        if self.state == F:
            return random.choice(STATES)
        else:
            return self.order

    def get_data(self):
        role = PRIMARY if self.port == self.primary_port else SECONDARY
        state = 'NF' if self.state == NF else 'F'
        return self.id, role, state, self.majority

    def run(self):
        ThreadedServer(self.rpc_service, port=self.port).start()
