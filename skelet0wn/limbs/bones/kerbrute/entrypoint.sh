#!/bin/sh

# Execute preliminary commands
# echo -e "workspace create test\nexit" | nxcdb

# Execute the main netexec command passed as arguments to the script
./kerbrute $@

# Execute the final command
