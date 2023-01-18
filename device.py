# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import time
import os
import logging
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from pyparsing import empty

#logging.basicConfig(level=logging.INFO)

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = 'HostName=RedeHibridaIoT.azure-devices.net;DeviceId=Teste1;SharedAccessKey=QWGWWSZJ+gStxB7TLBqVyWyrv02yYadCRsMYizewDjE='

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{"temperature": {temperature}, "humidity": 50, "battery": 100}}'

INTERVAL = 5

def create_client():
    # Create an IoT Hub client

    model_id = "dtmi:com:example:NonExistingController;1"

    client = IoTHubDeviceClient.create_from_connection_string(
                CONNECTION_STRING,
                product_info=model_id,
                websockets=True)  # used for communication over websockets (port 443)
    
    # *** Device Twin ***
    #
    # define behavior for receiving a twin patch
    # NOTE: this could be a function or a coroutine
    def twin_patch_handler(twin):
        global INTERVAL
        INTERVAL = twin['telemetryConfig']['interval'] // 1000
        
    try:

        # Attach the Device Twin Desired properties change request handler
        client.on_twin_desired_properties_patch_received = twin_patch_handler

        client.connect()

    except:
        # Clean up in the event of failure
        client.shutdown()
        raise

    return client


def run_telemetry_sample(client):
    # This sample will send temperature telemetry every second
    print("IoT Hub device sending periodic messages")

    client.connect()

    while True:
        # *** Sending a message ***
        #
        # Build the message with simulated telemetry values.
        temperature = os.popen('cat /sys/devices/virtual/thermal/thermal_zone0/temp').read()[0:2]
        msg_txt_formatted = MSG_TXT.format(temperature=temperature)
        message = Message(msg_txt_formatted)

        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        # Send the message.
        print(f"Sending message: {message}")
        client.send_message(message)

        print(f"Next message in: {INTERVAL} segundos")
        time.sleep(INTERVAL)


def main():
    print ("IoT Hub Quickstart #2 - Simulated device")
    print ("Press Ctrl-C to exit")

    # Instantiate the client. Use the same instance of the client for the duration of
    # your application
    client = create_client()

    # Send telemetry
    try:
        run_telemetry_sample(client)
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped by user")
    finally:
        print("Shutting down IoTHubClient")
        client.shutdown()


if __name__ == '__main__':
    main()