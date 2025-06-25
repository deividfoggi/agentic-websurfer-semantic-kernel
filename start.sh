#!/bin/bash
# Start the MCP server in the background
npx @playwright/mcp@latest --port 9339 --isolated --headless --no-sandbox --browser chrome &
MCP_PID=$!

# Give MCP server a moment to start
sleep 2

# Wait for MCP server to be available on 127.0.0.1 or 0.0.0.0
while true; do
  echo "Checking MCP server on 127.0.0.1:9339..."
  nc -z 127.0.0.1 9339 && break
  echo "Checking MCP server on 0.0.0.0:9339..."
  nc -z 0.0.0.0 9339 && break
  echo "Waiting for MCP server to start on port 9339..."
  sleep 1
done

echo "MCP server is up. Starting the main app."

python3 /app/src/main.py
