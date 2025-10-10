#!/bin/bash

# Fix dpkg database corruption
# This script attempts to repair corrupted dpkg database files

echo "=== Fixing dpkg database corruption ==="

# Backup corrupted files
echo "Creating backup of dpkg info directory..."
sudo mkdir -p /var/lib/dpkg/info.backup
sudo cp -a /var/lib/dpkg/info/* /var/lib/dpkg/info.backup/ 2>/dev/null || true

# Remove corrupted file
echo "Removing corrupted package info file..."
sudo rm -f /var/lib/dpkg/info/libupower-glib3:amd64.list

# Try to reinstall the package to restore the list file
echo "Attempting to restore package info..."
sudo apt-get install --reinstall libupower-glib3 -y 2>/dev/null || {
    echo "Could not reinstall package. Trying alternative fix..."
    sudo dpkg --remove --force-remove-reinstreq libupower-glib3 2>/dev/null || true
}

# Configure any unconfigured packages
echo "Configuring packages..."
sudo dpkg --configure -a

# Clean apt cache
echo "Cleaning apt cache..."
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo mkdir -p /var/lib/apt/lists/partial
sudo apt-get update

# Fix broken dependencies
echo "Fixing broken dependencies..."
sudo apt-get install -f -y

echo "=== dpkg fix complete ==="
echo "You can now try running the start script again."
