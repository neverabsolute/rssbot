#!/bin/bash

# Start main.py in the background
python main.py &
MAIN_PID=$!

# Start server.py in the background
python server.py &
SERVER_PID=$!

# Wait for either process to exit and then exit the entrypoint script with an error
wait -n
EXIT_STATUS=$?

# Kill the remaining processes if one exits
kill $MAIN_PID 2>/dev/null
kill $BOT_PID 2>/dev/null

# Exit with the captured exit status
exit $EXIT_STATUS