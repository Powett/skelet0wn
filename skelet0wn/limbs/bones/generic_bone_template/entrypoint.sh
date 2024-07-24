#!/bin/sh

# Template entrypoint script provided to ease integration of new skelet0wn tools

# Execute preliminary commands, if needed


# Execute the main netexec command passed as arguments to the script
tac $@ > generic_output.txt

# Execute the final commands, if needed
