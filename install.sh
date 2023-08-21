#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run with sudo."
    exit 1
fi

# Install python requirements 
echo "Installing Python Requirements"
pip install -r requirements.txt
echo "Installed Python Requirements"

# Install docker if not present
if ! command -v docker; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
    sudo systemctl enable docker
    echo "Finished docker installation."
fi

# Install docker-compose if not present
if ! command -v docker-compose; then
    echo "Installing Docker-compose..."
    sudo pip3 install docker-compose
    echo "Finished docker-compose installation."
fi