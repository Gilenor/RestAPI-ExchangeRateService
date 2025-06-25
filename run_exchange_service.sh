#! /bin/bash

export HOST_NAME=localhost
export SERVER_PORT=8080

python3 ./fill_database.py
python3 ./exchange_service.py
