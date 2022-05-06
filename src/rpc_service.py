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
