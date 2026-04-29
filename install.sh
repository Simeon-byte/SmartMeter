#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Bitte starte das Skript mit: sudo ./install.sh"
    exit 1
fi

ACTUAL_USER=${SUDO_USER:-$USER}

echo "--- Starte SmartMeter Installation ---"

# Docker installieren
if ! command -v docker &> /dev/null; then
    echo "[*] Installiere Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # User zur Docker-Gruppe hinzufügen
    usermod -aG docker "$ACTUAL_USER"
    echo "[✓] Docker installiert und User '$ACTUAL_USER' zur Gruppe hinzugefügt."
else
    echo "[i] Docker ist bereits installiert."
fi

echo "[*] Erstelle Datenverzeichnisse..."
if ! [ -d "./data/influxDB"]; then
    mkdir data/influxDB
fi

echo "[*] Setze Berechtigungen für ./data..."
chown -R "$ACTUAL_USER":"$ACTUAL_USER" "./data"
if [ -f "requirements.txt" ]; then
    echo "[?] Möchtest du die Python-Abhängigkeiten auch lokal installieren?"
    echo "    (Nur nötig für den Betrieb OHNE Docker)"
    read -p "Installieren? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[*] Erstelle Virtual Environment..."
        apt-get update && apt-get install -y python3-venv
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo "[✓] Python-Umgebung in ./venv bereit."
    fi
fi

echo "----------------------------------------------------"
echo "INSTALLATION ABGESCHLOSSEN"
echo "----------------------------------------------------"
echo "WICHTIG: Damit Docker ohne 'sudo' funktioniert,"
echo "logge dich bitte einmal aus und wieder ein (oder starte neu)."
echo "Danach kannst du mit 'docker compose up -d' starten."