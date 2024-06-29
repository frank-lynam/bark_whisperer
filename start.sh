#!/bin/bash

source .venv/bin/activate
uvicorn bw:bw --host 0.0.0.0 --port 8001
