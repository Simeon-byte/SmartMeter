#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run with sudo."
    exit 1
fi

# Install python requirements and docker, if not present
echo "Installing Python Requirements"
pip install -r requirements.txt

if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
    echo "Finished docker installation."
fi