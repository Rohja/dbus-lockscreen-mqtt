#!/bin/bash

SERVICENAME="Lockscreen2MQTT"

# Check if the directory ~/.config/systemd/user exists
if [ ! -d "~/.config/systemd/user" ]; then
    echo "Creating directory ~/.config/systemd/user"
    mkdir -p ~/.config/systemd/user
fi

# Copy the service file to ~/.config/systemd/user/$SERVICENAME.service
echo "Copying Lockscreen2MQTT.service to ~/.config/systemd/user"
cp -v systemd.service ~/.config/systemd/user/$SERVICENAME.service

# Enable the service
echo "Enabling $SERVICENAME.service"
systemctl --user enable $SERVICENAME.service

# Start the service
echo "Starting $SERVICENAME.service"
systemctl --user restart $SERVICENAME.service

# Check the status of the service
echo "Checking status of $SERVICENAME.service"
systemctl --user status $SERVICENAME.service

journalctl --user-unit  Lockscreen2MQTT | tail -n 40