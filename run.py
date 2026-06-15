#!/usr/bin/env python3
from app import create_app, create_socketio

app = create_app()
socketio = create_socketio()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
