# Temperature Sensor WebSocket App

This project is a real-time temperature monitoring application built with Flask, Flask-SocketIO, and WebSockets. It connects to a Ditto WebSocket server, receives temperature data from a simulated or real temperature sensor, and displays this data on a simple frontend interface.

## Features

- **Real-Time Data Streaming**
- **WebSocket Integration**
- **Frontend Display**

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:3000`.

3. **Access the Frontend**:
   Open a web browser and go to `http://localhost:3000` to view the temperature data in real-time.
