#!/usr/bin/env bash

if [ ! -d "venv" ] 
then
    echo "set-up venv"
    sudo apt-get install python3-venv -y
    python3 -m venv venv
    pip install --upgrade pip
    pip3 install pytest
    pip3 install flake8
fi

if [ -d "venv" ] 
then
    echo "Activate venv"
    source venv/bin/activate
    pip install -r requirements.txt
fi