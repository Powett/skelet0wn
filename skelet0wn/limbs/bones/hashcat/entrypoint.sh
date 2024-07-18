#!/bin/bash

# Execute preliminary commands


# Execute the main command
hashcat $@
# hashcat returns non-zero if exhausted
code=$?
chmod o+rw /mnt/skelet0wn/output.txt
if (( $code < 0 )); then
    exit $code
else
    exit 0
fi
# Execute the final commands
