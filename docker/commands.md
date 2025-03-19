# To Create a Policy in Ditto

```
curl -X PUT "http://localhost:8080/api/2/policies/smart-building:weather-sensor-policy" \
-u 'ditto:ditto' \
-H "Content-Type: application/json" \
-d '{
  "policyId": "smart-building:weather-sensor-policy",
  "entries": {
    "owner": {
      "subjects": {
        "nginx:ditto": {
          "type": "nginx basic auth user"
        }
      },
      "resources": {
        "thing:/": {
          "grant": [
            "READ",
            "WRITE"
          ],
          "revoke": []
        },
        "policy:/": {
          "grant": [
            "READ",
            "WRITE"
          ],
          "revoke": []
        },
        "message:/": {
          "grant": [
            "READ",
            "WRITE"
          ],
          "revoke": []
        }
      }
    },
    "connection": {
      "subjects": {
        "connection:mqtt": {
          "type": "Connection to MQTT broker"
        }
      },
      "resources": {
        "thing:/": {
          "grant": [
            "READ",
            "WRITE"
          ],
          "revoke": []
        },
        "message:/": {
          "grant": [
            "READ",
            "WRITE"
          ],
          "revoke": []
        }
      }
    }
  }
}'

```

# To Create a Thing for the Weather Sensor

```
curl -X PUT "http://localhost:8080/api/2/things/smart-building:weather-sensor" \
-u 'ditto:ditto' \
-H "Content-Type: application/json" \
-d '{
    "thingId": "smart-building:weather-sensor",
    "policyId": "smart-building:weather-sensor-policy",
    "attributes": {
        "manufacturer": "Raspberry Pi",
        "model": "Weather Sensor",
        "location": "Building A, Room 101"
    },
    "features": {
        "temperature": {
            "properties": {
                "value": 0
            }
        },
        "humidity": {
            "properties": {
                "value": 0
            }
        }
    }
}'

```

# To Create Connection with JavaScript Payload Mapping

```
curl -X PUT \
  "http://localhost:8080/api/2/connections/aa373b49-9a9e-4dd2-952e-9326eefa5b05" \
  -H "Content-Type: application/json" \
  -u 'devops:foobar' \
  -d '{
    "name": "Mosquitto Connection",
    "connectionType": "mqtt-5",
    "connectionStatus": "open",
    "uri": "tcp://docker-mosquitto-1:1883",
    "sources": [
      {
        "addresses": [
          "devices/+"
        ],
        "consumerCount": 1,
        "qos": 1,
        "authorizationContext": [
          "connection:mqtt"
        ],
        "enforcement": {
          "input": "{{ source:address }}",
          "filters": [
            "devices/{{ thing:name }}"
          ]
        },
        "headerMapping": {
          "content-type": "{{header:content-type}}",
          "reply-to": "{{header:reply-to}}",
          "correlation-id": "{{header:correlation-id}}"
        },
        "payloadMapping": [
          "javascript"
        ],
        "replyTarget": {
          "address": "{{header:reply-to}}",
          "headerMapping": {
            "content-type": "{{header:content-type}}",
            "correlation-id": "{{header:correlation-id}}"
          },
          "expectedResponseTypes": [
            "response",
            "error"
          ],
          "enabled": true
        }
      }
    ],
    "targets": [
      {
        "address": "devices/{{ thing:id }}/downlink",
        "topics": [
          "_/_/things/twin/events"
        ],
        "qos": 1,
        "authorizationContext": [
          "connection:mqtt"
        ],
        "headerMapping": {
          "reply-to": "devices/{{ thing:name }}/downlink",
          "correlation-id": "{{ header:correlation-id }}",
          "Content-Type": "application/vnd.eclipse.ditto+json"
        },
        "payloadMapping": [
          "Ditto"
        ]
      }
    ],
    "clientCount": 1,
    "failoverEnabled": true,
    "validateCertificates": true,
    "processorPoolSize": 1,
    "mappingDefinitions": {
      "javascript": {
        "mappingEngine": "JavaScript",
        "options": {
          "incomingScript": "function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {\n    const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload));\n    const jsonData = JSON.parse(jsonString); \n    \n    // Parse the thingId and individual sensor values\n    const thingId = jsonData.thingId.split(':'); \n    const value = { \n        temperature: { \n            properties: { \n                value: jsonData.temperature \n            } \n        },\n        humidity: { \n            properties: { \n                value: jsonData.humidity \n            } \n        }   \n    };    \n\n    return Ditto.buildDittoProtocolMsg(\n        thingId[0], // namespace\n        thingId[1], // thing name\n        'things', // thing type\n        'twin', // update the twin\n        'commands', // command to update twin\n        'modify', // modify the twin data\n        '/features', // target all features\n        headers, \n        value\n    );\n}\n",
          "outgoingScript": ""
        }
      }
    },
    "tags": []
  }'

```

## manually publish sensor data to mqtt server

```
mosquitto_pub -h localhost -p 1883 -t "devices/weather-sensor" -m '{"temperature": 24.5, "humidity": 70, "thingId": "smart-building:weather-sensor"}' -V mqttv5

```

## varify message publishing or not via mqtt

```
mosquitto_sub -h localhost -p 1883 -t "devices/weather-sensor" -v
```

```
mosquitto_pub -h localhost -p 1883 -t "devices/light-sensor" -m '{"thingId":"smart-building:light-sensor","brightness":300}' -V mqttv5

```


curl -X POST "http://localhost:8080/api/2/things/smart-building:weather-sensor/inbox/messages/control"      -u "ditto:ditto"      -H "Content-Type: application/json"      -d '{
       "headers": {},
       "path": "/",
       "value": {
         "action": "turn_on_fan",
         "temperatureThreshold": 25
       }
     }'

     



Previous target

targets": [
    {
      "address": "devices/{{ thing:id }}/downlink",
      "topics": [
        "_/_/things/twin/events"
      ],
      "qos": 1,
      "authorizationContext": [
        "connection:mqtt"
      ],
      "headerMapping": {
        "reply-to": "devices/weather-sensor/downlink",
        "correlation-id": "{{ header:correlation-id }}",
        "Content-Type": "application/vnd.eclipse.ditto+json"
      },
      "payloadMapping": [
        "Ditto"
      ]
    }
  ],


# update connection for handling downlink (outbound request) 
function mapFromDittoProtocolMsg(dittoHeaders, textPayload, bytePayload, contentType) {
    const jsonPayload = JSON.parse(textPayload);
    const topic = dittoHeaders["topic"];

    // Check if it's a twin events message (updated value)
    if (topic && topic.endsWith("/things/twin/events")) {
        const thingId = jsonPayload["thingId"];
        const features = jsonPayload["features"];

        const payloadToSend = {
            thingId: thingId,
            features: features
        };

        return {
            headers: {
                "content-type": "application/json"
            },
            payload: JSON.stringify(payloadToSend)
        };
    }

    // Default fallback
    return {
        headers: {
            "content-type": "application/json"
        },
        payload: JSON.stringify({ message: "Unhandled event" })
    };
}


# Update ditto from third party app (python flask or arrowhead service )
  curl -X PUT \
  -u ditto:ditto \
  "http://localhost:8080/api/2/things/smart-building:weather-sensor/features/temperature/properties/value" \
  -H "Content-Type: application/json" \
  -d "27.6"


  curl -X PUT \
  -u ditto:ditto \
  "http://localhost:8080/api/2/things/smart-building3:motion-sensor/features/motion/properties/value" \
  -H "Content-Type: application/json" \
  -d "false"

# check updated data to respberry pi sent from ditto triggered by third party app or arrowhead service 
mosquitto_sub -h localhost -t "devices/weather-sensor/downlink" -v
