PORT = 18812

ACTUAL_ORDER = "actual-order"
G_STATE = "g-state"
G_KILL = "g-kill"
G_ADD = "g-add"
EXIT = "exit"

PRIMARY = "primary"
SECONDARY = "secondary"

ATTACK = "attack"
RETREAT = "retreat"
ORDERS = [ATTACK, RETREAT]

F = "faulty"
NF = "non-faulty"
STATES = [NF, F]

UNDEFINED = "undefined"

COMMANDS = {
    ACTUAL_ORDER: "actual-order <order> - proposes an order ('attack'/'retreat') to the primary",
    G_STATE: "g-state <id> <state> - set state ('faulty'/'non-faulty') to general by id\ng-state - show generals list",
    G_KILL: "g-kill <id> - remove general by id",
    G_ADD: "g-add K - add K generals"
}
