'''pip install paho-mqtt RPi.GPIO'''

import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json
import logging

# Configuration
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO
broker = 'localhost'  # MQTT broker address (use 'localhost' if on the same device)
port = 1883  # MQTT broker port
topic = 'devices/water-level-sensor'  # Topic to publish sensor data
data_interval = 10  # Time interval between data readings in seconds

# Set up logging
logging.basicConfig(
    filename='water_level_mqtt_publisher.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# MQTT client setup
client = mqtt.Client()
client.connect(broker, port, 60)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    """Measures distance using HC-SR04 ultrasonic sensor."""
    # Send a 10us pulse to trigger the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    # Measure the time between the send and receive pulses
    start_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    # Calculate distance
    duration = end_time - start_time
    distance = (duration * 34300) / 2  # Speed of sound = 34300 cm/s, divide by 2 for round trip
    return distance

def publish_water_level(distance):
    """Formats and publishes water level data as a JSON message via MQTT."""
    # Create JSON message payload
    payload = {
        "distance": distance,
        "thingId": "smart-building:water-level-sensor"
    }
    # Convert the payload to JSON format
    payload_json = json.dumps(payload)
    
    # Publish to MQTT topic
    result = client.publish(topic, payload_json, qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Data published to topic '{topic}': {payload_json}")
    else:
        logging.error(f"Failed to publish data to topic '{topic}'. Error code: {result.rc}")

def main():
    logging.info("Starting water level data collection and MQTT publishing")

    try:
        while True:
            distance = measure_distance()
            if distance is not None:
                publish_water_level(distance)
                print(f"Published data: Distance to water = {distance:.2f} cm")
            else:
                logging.warning("Received None values from the sensor.")

            # Wait for the specified interval
            time.sleep(data_interval)
    except KeyboardInterrupt:
        logging.info("Data collection and publishing stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        client.disconnect()

if __name__ == "__main__":
    main()
