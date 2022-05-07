import readline
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


def signal_handler(sig, frame):
    for n in nodes:
        n.terminate()
    print("Exiting...")
    exit(0)

def print_generals_data(ports, flag=False):
    for port in ports:
            conn = rpyc.connect("localhost", port)
            id, role, state, majority = conn.root.get_node_data()
            print(f"G{id},{role},state={state}" + f"{',majority=' + majority if flag else ''}")
            conn.close()


generals_number = int(sys.argv[1])

nodes = []
ports = list(range(PORT, PORT + generals_number))

for n in range(generals_number):
    node = Node(PORT + n, ports.copy())
    node.primary_port = PORT
    nodes.append(node)

for node in nodes:
    node.start()

for description in COMMANDS.values():
    print(description)

signal.signal(signal.SIGINT, signal_handler)

while True:

    command = input("\nCommand: ").split()

    if not is_command_valid(command):
        print("Command is invalid. Please try again.")
        continue
    elif command[0] == ACTUAL_ORDER:
        conn = rpyc.connect("localhost", ports[0])
        response = conn.root.define_order(order=command[1])
        conn.close()

        print_generals_data(ports, True)

        print(response)
    elif command[0] == G_STATE:
        if len(command) == 3:
            conn = rpyc.connect("localhost", PORT + int(command[1]) - 1)
            conn.root.set_state(state=command[2])
            conn.close()

        print_generals_data(ports, False)
    elif command[0] == G_KILL:
        id = int(command[1])
        port = PORT + id - 1
        if port in ports:
            conn = rpyc.connect("localhost", port)
            conn.root.kill_general(port)
            conn.close()

            for node in nodes:
                if node.id == id:
                    node.terminate()
                    nodes.remove(node)
                    break

            ports.remove(port)
            print_generals_data(ports, False)
        else:
            print(f"No general with id {port % PORT + 1}.")
    elif command[0] == G_ADD:
        generals_to_add = int(command[1])
        new_ports = list(range(ports[-1] + 1, ports[-1] + 1 + generals_to_add))
        for port in new_ports:
            ports.append(port)
        
        for port in new_ports:
            node = Node(port, ports.copy())
            nodes.append(node)
            node.start()

        conn = rpyc.connect("localhost", ports[0])
        conn.root.add_generals(new_ports)
        conn.close()

        print_generals_data(ports, False)
    elif command[0] == "exit":
        print("Exiting...")
        break

for n in nodes:
    n.terminate()

exit(0)
