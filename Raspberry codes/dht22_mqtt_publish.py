'''
pip install Adafruit_DHT
pip install paho-mqtt

'''
import Adafruit_DHT
import paho.mqtt.client as mqtt
import json
import time
import logging

# Configuration
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin connected to the DHT22 sensor data pin
broker = 'localhost'  # MQTT broker address (use 'localhost' if on the same device)
port = 1883  # MQTT broker port
topic = 'devices/weather-sensor'  # Topic to publish sensor data
data_interval = 10  # Time interval between data readings in seconds

# MQTT client setup
client = mqtt.Client()
client.connect(broker, port, 60)

# Set up logging
logging.basicConfig(
    filename='dht22_mqtt_publisher.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_dht22_data():
    """Reads temperature and humidity data from DHT22 sensor."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return humidity, temperature
    else:
        logging.error("Failed to retrieve data from DHT22 sensor.")
        return None, None

def publish_sensor_data(humidity, temperature):
    """Formats and publishes sensor data as a JSON message via MQTT."""
    # Create JSON message payload
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "thingId": "smart-building:temperature-sensor"
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
    logging.info("Starting DHT22 data collection and MQTT publishing")
    
    try:
        while True:
            # Get sensor data
            humidity, temperature = get_dht22_data()
            
            # Check if data is valid before publishing
            if humidity is not None and temperature is not None:
                publish_sensor_data(humidity, temperature)
                print(f"Published data: Temperature = {temperature:.2f}°C, Humidity = {humidity:.2f}%")
            else:
                logging.warning("Received None values from DHT22 sensor.")

            # Wait for the specified interval
            time.sleep(data_interval)
    except KeyboardInterrupt:
        logging.info("Data collection and publishing stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
