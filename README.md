# ds-project-2

-------------------

### Instructions (Tested in Linux)

To be able to run this project, you need to have Python installed and execute the following command:

```
./Generals_Byzantine_program.sh N
```
N - number of processes (N > 0).

This command first creates a virtual environment (`env` folder) if it does not exist and then installs the requirements. Afterwards, the main.py script is run automatically.

### Notes

Each node represents a process which is "connected" to an RPC service by port. RPC service is used to perform communication.
For each node, the majority property is the order majority collected from other nodes.
For example, if primary process collected two 'attack' orders and one 'retreat' order, its majority property is equal to 'attack'.

### Group

* Elizaveta Nikolaeva
* Dariya Nagashibayeva