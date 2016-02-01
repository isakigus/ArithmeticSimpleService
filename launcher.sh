#!/bin/bash

HOST=127.0.0.1
PORT=12345
FILE_INPUT=operations.7z
# FILE_INPUT=operations.txt
FILE_OUTPUT=operations_output.txt


virtualenv pitagoras
./pitagoras/bin/pip install -r requirements
./pitagoras/bin/python service.py --host $HOST --port $PORT &
#./pitagoras/bin/python service.py --verbose --host $HOST --port $PORT &

# give time to the server to start
sleep 5

./pitagoras/bin/python client.py --host $HOST --port $PORT \
--output-file $FILE_OUTPUT \
--input-file $FILE_INPUT
