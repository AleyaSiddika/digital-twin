function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    try {
        // Ensure that the payload is a valid JSON string
        const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload));
        const jsonData = JSON.parse(jsonString);
        
        // Check for the presence of 'thingId' and 'brightness'
        if (!jsonData.thingId || !jsonData.brightness) {
            throw new Error('Missing required fields: thingId or brightness');
        }
        
        // Parse the thingId correctly
        const thingId = jsonData.thingId.split(':');
        
        // Ensure thingId is valid
        if (thingId.length !== 2) {
            throw new Error('Invalid thingId format');
        }

        const value = {
            brightness: {
                properties: {
                    value: jsonData.brightness
                }
            }
        };

        return Ditto.buildDittoProtocolMsg(
            thingId[0], // namespace
            thingId[1], // thing name
            'things', // thing type
            'twin', // update the twin
            'commands', // command to update twin
            'modify', // modify the twin data
            '/features', // target all features
            headers,
            value
        );
    } catch (error) {
        return Ditto.buildDittoProtocolMsg(
            'error', // namespace for error
            'error', // thing name for error
            'things',
            'twin',
            'commands',
            'modify',
            '/features',
            headers,
            { error: error.message }
        );
    }
}



{
  "id": "4098f215-fa1f-4b6d-84f5-86ea85861ec5",
  "name": "Light Connection",
  "connectionType": "mqtt-5",
  "connectionStatus": "open",
  "uri": "tcp://docker-mosquitto-1:1883",
  "sources": [
    {
      "addresses": [
        "devices/light-sensor"
      ],
      "consumerCount": 1,
      "qos": 1,
      "authorizationContext": [
        "connection:mqtt"
      ],
      "enforcement": {
        "input": "{{ source:address }}",
        "filters": [
          "devices/light-sensor"
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
        "reply-to": "devices/weather-sensor/downlink",
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
        "incomingScript": "function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {\n    const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload));\n    const jsonData = JSON.parse(jsonString);\n\n    console.log(\"Received Thing ID:\", jsonData.thingId);\n    console.log(\"Source Address:\", headers[\"mqtt.topic\"]);\n\n    if (jsonData.thingId !== \"ditto-building:light-sensor\") {\n        return null;  // Ignore weather sensor messages in light sensor connection\n    }\n\n    const thingId = jsonData.thingId.split(':');\n    const value = {\n        brightness: {\n            properties: {\n                value: jsonData.brightness\n            }\n        }\n    };\n\n    return Ditto.buildDittoProtocolMsg(\n        thingId[0], \n        thingId[1], \n        'things', \n        'twin', \n        'commands', \n        'modify', \n        '/features', \n        headers, \n        value\n    );\n}",
        "outgoingScript": ""
      }
    }
  },
  "tags": []
}