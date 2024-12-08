'''pip install paho-mqtt spidev
'''
import spidev
import time
import paho.mqtt.client as mqtt
import json
import logging

# Configuration
broker = 'localhost'  # MQTT broker address (use 'localhost' if on the same device)
port = 1883  # MQTT broker port
topic = 'devices/light-sensor'  # Topic to publish sensor data
data_interval = 10  # Time interval between data readings in seconds
mcp3008_channel = 0  # Channel on MCP3008 where the LDR is connected

# Set up logging
logging.basicConfig(
    filename='light_sensor_mqtt_publisher.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# MQTT client setup
client = mqtt.Client()
client.connect(broker, port, 60)

# SPI setup for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CE0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    """Reads the raw value from the specified channel on the MCP3008."""
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0 and 7")
    
    # Perform SPI transaction and store returned bits
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    
    # Extract 10-bit ADC value from returned bits
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_light_level(adc_value):
    """Converts ADC reading to a light level percentage (0-100%)."""
    return (adc_value / 1023) * 100

def publish_light_level(light_level):
    """Formats and publishes light level data as a JSON message via MQTT."""
    payload = {
        "light_level": light_level,
        "thingId": "smart-building:light-sensor"
    }
    payload_json = json.dumps(payload)
    
    result = client.publish(topic, payload_json, qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Data published to topic '{topic}': {payload_json}")
    else:
        logging.error(f"Failed to publish data to topic '{topic}'. Error code: {result.rc}")

def main():
    logging.info("Starting light level data collection and MQTT publishing")

    try:
        while True:
            # Read raw data from MCP3008
            adc_value = read_adc(mcp3008_channel)
            light_level = convert_to_light_level(adc_value)
            
            # Publish light level data
            publish_light_level(light_level)
            print(f"Published data: Light Level = {light_level:.2f}%")
            
            # Wait for the specified interval
            time.sleep(data_interval)
    except KeyboardInterrupt:
        logging.info("Data collection and publishing stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        spi.close()
        client.disconnect()

if __name__ == "__main__":
    main()
