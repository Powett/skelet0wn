#!/bin/sh

# Execute preliminary commands


# Execute the main netexec command passed as arguments to the script
nmap $@
chmod a+rw -R /mnt/skelet0wn/

# Execute the final commands
