from app import create_app, create_socketio, socketio

app = create_app()
# expose socketio as server entrypoint
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
