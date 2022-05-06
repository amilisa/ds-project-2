#!/bin/bash

re='^[+-]?[0-9]+([.][0-9]+)?$'
if ! [[ "$1" =~ $re ]] || [ -z "$1" -o $1 -lt 1 ]; then
printf "Usage: run.sh [N]: N number of processes (N > 0)\n"
exit 1
fi

if ! [[ -f ./env/bin/python3 ]]
then
echo "Creating a virtual env..."
python3 -m venv env
alias activate=". ../.env/bin/activate"
fi

echo "Installing the requirements..."
./env/bin/pip3 install -r ./requirements.txt
echo "Starting the processes..."
./env/bin/python3 ./src/main.py $1
