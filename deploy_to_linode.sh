#!/bin/bash

# Deploy Script for Sentinel-V2 on Linode/Ubuntu
# Usage: ./deploy_to_linode.sh

echo "Starting deployment setup..."

# 1. Update System
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker & Docker Compose
echo "Installing Docker..."
if ! command -v docker &> /dev/null
then
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    echo "Docker already installed."
fi

# 3. Pull/Build and Run
echo "Building and running container..."
# Assumes this script is run inside the repo directory on the server
# or after git cloning.

# Check if .env exists, if not warn user
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Ensure DEEPGRAM_API_KEY is set in environment or create .env file."
fi

sudo docker compose up -d --build

echo "Deployment complete! App should be running on port 5000."
