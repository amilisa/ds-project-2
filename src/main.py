import sys
import rpyc
import signal
from node import Node
from consts import PORT, COMMANDS, ACTUAL_ORDER, G_STATE, G_KILL, G_ADD, ORDERS, STATES


def is_command_valid(command):
    args_number = len(command)
    if command[0] in COMMANDS:
        if command[0] == ACTUAL_ORDER and args_number == 2 and command[1] in ORDERS:
            return True
        elif command[0] == G_STATE and args_number == 1:
            return True
        elif command[0] == G_STATE and args_number == 3 and command[1].isdigit() and command[2] in STATES:
            return True
        elif (command[0] == G_KILL or command[0] == G_ADD) and command[1].isdigit():
            return True
    return False


processes_number = int(sys.argv[1])

nodes = []

for n in range(processes_number):
    node = Node(PORT + n, processes_number)
    if n == 0:
        node.is_primary = True
    node.primary_port = PORT
    nodes.append(node)

for node in nodes:
    node.generals = nodes
    node.start()

for description in COMMANDS.values():
    print(description)


def signal_handler(sig, frame):
    for n in nodes:
        n.terminate()
    print("Exiting...")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

while True:

    command = input("\nCommand: ").split()

    if not is_command_valid(command):
        print("Command is invalid. Please try again.")
        continue
    elif command[0] == ACTUAL_ORDER:
        conn = rpyc.connect("localhost", nodes[0].port)
        response = conn.root.define_order(order=command[1])
        conn.close()

        for node in nodes:
            conn = rpyc.connect("localhost", node.port)
            id, role, state, majority = conn.root.get_node_data()
            print(f"G{id},{role},state={state},majority={majority}")
            conn.close()

        print(response)
    elif command[0] == G_STATE:
        # TODO: g-state
        pass
    elif command[0] == G_KILL:
        # TODO: g-kill
        pass
    elif command[0] == G_ADD:
        # TODO: g-add
        pass
    elif command[0] == "exit":
        print("Exiting...")
        break

for n in nodes:
    n.terminate()

exit(0)
