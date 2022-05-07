import rpyc
import random
from multiprocessing import Process
from consts import PORT, NF, F, PRIMARY, SECONDARY, ATTACK, RETREAT, UNDEFINED, ORDERS
from rpc_service import RPCService
from rpyc.utils.server import ThreadedServer


class Node(Process):
    def __init__(self, port, ports):
        super().__init__()
        self.id = port % PORT + 1
        self.port = port
        self.ports = ports
        self.generals_number = len(self.ports)
        self.ports.remove(self.port)
        self.primary_port = None
        self.state = NF
        self.majority = None
        self.order = None
        self.faulty_generals_number = 0
        self.rpc_service = RPCService(self)

    def define_order(self, order):
        for port in self.ports:
            if self.state == F:
                self.set_order(random.choice(ORDERS))
            else:
                self.set_order(order)
            conn = rpyc.connect("localhost", port)
            conn.root.set_order(self.order)
            conn.close()

        votes = {ATTACK: 0, RETREAT: 0}
        for port in self.ports:
            conn = rpyc.connect("localhost", port)
            response = conn.root.perform_quorum()
            conn.close()
            if response != UNDEFINED:
                votes[response] += 1

        if self.generals_number < 3 * self.faulty_generals_number + 1:
            self.majority = UNDEFINED
            return f"Execute order: cannot be determined - not enough generals in the system! " + \
                f"{self.faulty_generals_number} faulty node in the system, " + \
                f"{self.generals_number - self.faulty_generals_number} out of {self.generals_number} quorum not consistent."
        else:
            order = max(votes, key=votes.get)
            quorum_number = self.generals_number - self.faulty_generals_number if self.state == F  \
                else self.generals_number - 1 - self.faulty_generals_number

            self.majority = order
            return f"Execute order: {order}! " + \
                f"{'Non-faulty' if self.faulty_generals_number == 0 else str(self.faulty_generals_number) + ' faulty'} nodes in the system, " + \
                f"{quorum_number} out of {self.generals_number} quorum suggest {order}."

    def set_order(self, order):
        self.order = order

    def set_state(self, state):
        self.state = state
        if self.state == NF and self.faulty_generals_number > 0:
            self.faulty_generals_number -= 1
        else:
            self.faulty_generals_number += 1

        for port in self.ports:
            conn = rpyc.connect("localhost", port)
            conn.root.set_faulty_generals_number(self.faulty_generals_number)
            conn.close()
        
    def set_faulty_generals_number(self, faulty_generals_number):
        self.faulty_generals_number = faulty_generals_number

    def perform_quorum(self):
        votes = {ATTACK: 0, RETREAT: 0}
        votes[self.order] += 1
        for port in self.ports:
            if port != self.primary_port:
                conn = rpyc.connect("localhost", port)
                order = conn.root.get_order()
                conn.close()
                votes[order] += 1

        if self.generals_number < 3 * self.faulty_generals_number + 1:
            self.majority = UNDEFINED
        else:
            self.majority = max(votes, key=votes.get)

        return self.majority

    def get_order(self):
        if self.state == F:
            return random.choice(ORDERS)
        else:
            return self.order

    def get_data(self):
        role = PRIMARY if self.port == self.primary_port else SECONDARY
        state = 'NF' if self.state == NF else 'F'
        return self.id, role, state, self.majority

    def kill_general(self, port):
        is_primary = port == self.primary_port
        for p in self.ports:
            conn = rpyc.connect("localhost", p)
            if is_primary:
                primary = sorted(self.ports)[0]
                conn.root.set_primary(primary)
            conn.root.remove_general(port, self.state)
            conn.close()
    
    def set_primary(self, primary):
        self.primary_port = primary
    
    def remove_general(self, port, state):
        self.ports.remove(port)
        self.generals_number -= 1
        if state == F:
            self.faulty_generals_number -= 1

    def add_generals(self, new_ports):
        if self.port == self.primary_port:
            for port in self.ports:
                conn = rpyc.connect("localhost", port)
                conn.root.add_generals(new_ports)
                conn.close()

            for port in new_ports:
                conn = rpyc.connect("localhost", port)
                conn.root.set_primary(self.primary_port)
                conn.root.set_faulty_generals_number(self.faulty_generals_number)
                conn.close()

        for port in new_ports:
            self.ports.append(port)
            self.generals_number += 1

    def run(self):
        ThreadedServer(self.rpc_service, port=self.port).start()
