#!/bin/sh

# Execute preliminary commands
# echo -e "workspace create test\nexit" | nxcdb

# Execute the main netexec command passed as arguments to the script
netexec $@

# Execute the final command
cp -r ~/.nxc/workspaces/default /mnt/skelet0wn/