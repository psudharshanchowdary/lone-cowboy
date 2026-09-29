#!/usr/bin/env bash
# 3D Lone Cowboy Web Launcher
# Starts a local web server and opens the 3D game in your browser

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8080
# Find an available port if 8080 is taken
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; do
    PORT=$((PORT + 1))
done

echo "====================================================="
echo "🤠 Starting Lone Cowboy 3D Web Game on port $PORT..."
echo "Open in browser: http://localhost:$PORT/web3d/index.html"
echo "Press Ctrl+C to stop the server."
echo "====================================================="

# Open browser on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$PORT/web3d/index.html"
elif command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:$PORT/web3d/index.html"
fi

python3 -m http.server $PORT
