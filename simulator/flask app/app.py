from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import websocket
import base64
import json
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for local development

# Ditto WebSocket URL and authentication setup
DITTO_URL = "ws://localhost:8080/ws/2"
AUTH_USERNAME = "ditto"
AUTH_PASSWORD = "ditto"
encoded_auth = base64.b64encode(f"{AUTH_USERNAME}:{AUTH_PASSWORD}".encode()).decode()

# Flask route to serve the frontend HTML
@app.route("/")
def index():
    return render_template("index.html")

# Function to handle messages from Ditto and emit to frontend
def on_ditto_message(ws, message):
    print("Received from Ditto:", message)
    try:
        data = json.loads(message)
        # Send the entire raw message to the frontend
        socketio.emit("weather_update", data)
    except Exception as e:
        print("Error forwarding message:", e)

# Function to initiate connection to Ditto WebSocket
def start_ditto_connection():
    def on_open(ws):
        subscribe_message = "START-SEND-EVENTS?filter=eq(/thingId,'smart-building:weather-sensor')"
        ws.send(subscribe_message)

    # Connect to Ditto WebSocket and receive events
    ws = websocket.WebSocketApp(
        DITTO_URL,
        header={"Authorization": f"Basic {encoded_auth}"},
        on_message=on_ditto_message,
        on_open=on_open
    )
    ws.run_forever()

# Start Ditto WebSocket in a separate thread
ditto_thread = threading.Thread(target=start_ditto_connection)
ditto_thread.daemon = True
ditto_thread.start()

# Start the Flask-SocketIO server
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
