import rpyc


class RPCService(rpyc.Service):
    def __init__(self, node):
        self.node = node
        super().__init__()

    def exposed_define_order(self, order):
        return self.node.define_order(order)

    def exposed_set_order(self, order):
        return self.node.set_order(order)

    def exposed_perform_quorum(self):
        return self.node.perform_quorum()

    def exposed_get_order(self):
        return self.node.get_order()

    def exposed_get_node_data(self):
        return self.node.get_data()

    def exposed_set_state(self, state):
        self.node.set_state(state)

    def exposed_set_faulty_generals_number(self, faulty_generals_number):
        self.node.set_faulty_generals_number(faulty_generals_number)

    def exposed_kill_general(self, port):
        self.node.kill_general(port)

    def exposed_set_primary(self, primary):
        self.node.set_primary(primary)

    def exposed_remove_general(self, port, state):
        self.node.remove_general(port, state)

    def exposed_add_generals(self, generals_number):
        self.node.add_generals(generals_number)