import os
import configparser
import requests
import paho.mqtt.client as mqtt
import logging
import time
from datetime import datetime, timezone

# Add and setup logging to a file in /root/mqtt which is also where  I  store the  script
logging.basicConfig(
    filename="/root/mqtt/mqtt.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.ERROR,
)
# uncomment to also log to stderr for testing
# logging.getLogger().addHandler(logging.StreamHandler())

logging.info("Running MQTT Publisher")

logger = logging.getLogger("MQTT")
# Other definitions including your broker address
han_host = os.getenv("HAN_API_HOST")
# Read in broker config from mqtt.cfg
config = configparser.ConfigParser()
config.read("mqtt.cfg")

if config.read("/root/mqtt/mqtt.cfg"):
    logger.info("Reading from config file " + str(config.read("/root/mqtt/mqtt.cfg")))
    broker = config.get("broker", "ip")
    port = config.get("broker", "port")
    logger.info("Using " + broker + " as the broker")
    logger.info("And " + str(port) + " as the port")
    # check for authentication section if it exists use authentication
    authentication = config.has_section("authentication")
    if authentication:
        logger.info("Using authentication as defined in mqtt.cfg")
        username = config.get("authentication", "username")
        password = config.get("authentication", "password")
    meters = config.has_section("meters")
    if meters:
        logger.info("Using meters as defined in mqtt.cfg")
        electricity_meter = config.get("meters", "electricity") == "True"
        gas_meter = config.get("meters", "gas") == "True"
    # catches issue if someone has not added a meter section to  meter.cfg
    else:
        logger.info("No meter section in mqtt.cfg, using default electricity")
        electricity_meter = True
        gas_meter = False
    logging = config.has_section("logging")
    if logging:
        log_level = config.get("logging", "level")
        try:
            logger.setLevel(log_level)
            logger.info("Setting Log Level to " + log_level)
        except:
            logger.info("Default  to error level logging")
else:
    logger.error("Config file mqtt.cfg not found, using defaults")
    broker = "192.168.1.41"
    port = 1883
    authentication = False
    electricity_meter = True
    gas_meter = False
# Create a flag in class to track MQTT broker connection success
mqtt.Client.connected_flag = False


def on_publish(
    client, userdata, mid, reason_codes, properties
):  # create function for callback
    logger.info("MQTT topic published")
    pass


def on_connect(client, userdata, flags, reason_code, properties):
    # if flags.session_present:
    # ...
    if reason_code == 0:
        # successful connection
        logger.info("Connected to MQTT Broker. Returned code = " + str(reason_code))
        client.connected_flag = True

    if reason_code > 0:
        # error processing
        logger.error(
            "Bad connection to MQTT Broker. Returned code = " + str(reason_code)
        )


def on_disconnect(client, userdata, flags, reason_code, properties):
    logger.info("Disconnected from MQTT broker  " + str(reason_code))
    client.connected_flag = False


def get_meter_consumption(meter_type):
    consump_response = requests.post(
        han_host + "/get_meter_consumption", json={"meter_type": meter_type}
    )
    if consump_response.ok:
        meter_consumption = consump_response.json()["meter_consump"]
        logger.info(f"{meter_type} consumption returned")
        return meter_consumption
    else:
        logger.error(
            f"Error calling {meter_type} get_meter_consumption API: {consump_response.json()['Status']}"
        )
        return {"error": consump_response.json()["Status"]}


def get_meter_status(meter_type):
    status_response = requests.post(
        han_host + "/get_meter_status", json={"meter_type": meter_type}
    )
    if status_response.ok:
        meter_status = status_response.json()["meter_status"]
        logger.info(f"{meter_type} meter status returned")
        return meter_status
    else:
        logger.error(
            f"Error calling {meter_type} get_meter_status API: {status_response.json()['Status']}"
        )
        return {"error": status_response.json()["Status"]}


def get_meter_info(meter_type):
    info_response = requests.post(
        han_host + "/get_meter_info", json={"meter_type": meter_type}
    )
    if info_response.ok:
        meter_info = info_response.json()["meter_info"]
        logger.info(f"{meter_type} meter info returned")
        return meter_info
    else:
        logger.error(
            f"Error calling {meter_type} get_meter_info API: {info_response.json()['Status']}"
        )
        return {"error": info_response.json()["Status"]}


#   start the client and define callbacks
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
if authentication:
    client.username_pw_set(username, password)
    logger.info(f"Using username {username} to authenticate")

logger.info("Connecting to Broker " + broker)
# Run the main loop
client.loop_start()
try:
    client.connect(broker, int(port), 60)
except:
    logger.info("Connection to " + broker + " failed")
while not client.connected_flag:  # wait in loop
    logger.warning("Waiting for Broker connection")
    time.sleep(1)
logger.info("Started Main Loop")
while True:
    # Check broker connection and wait for reconnect
    if client.connected_flag:
        pass
    else:
        while not client.connected_flag:  # wait in loop
            logger.info("Waiting for Broker connection")
            time.sleep(5)
    # set timestamp for this update loop
    current_timestamp = str(datetime.now(timezone.utc).replace(tzinfo=None))
    logger.info("Update cycle started " + current_timestamp)

    # Get elec meter consumption
    if electricity_meter:
        elec_meter_consumption = get_meter_consumption("elec")
        elec_meter_status = get_meter_status("elec")
        elec_meter_info = get_meter_info("elec")

        # still publish to original topics for backward compatibility
        try:
            client.publish("homepro/elec_meter", elec_meter_consumption)
            client.publish("homepro/elect_meter_status", elec_meter_status)

            client.publish("homepro/elec_meter/consumption", elec_meter_consumption)
            client.publish("homepro/elec_meter/status", elec_meter_status)
            client.publish("homepro/elec_meter/info", elec_meter_info)
        except:
            logging.error("Error publishing electricity to MQTT")

    # Get gas meter consumption
    if gas_meter:
        gas_meter_consumption = get_meter_consumption("gas")
        gas_meter_status = get_meter_status("gas")
        gas_meter_info = get_meter_info("gas")

        # still publish to original topics for backward compatibility
        try:
            client.publish("homepro/gas_meter", gas_meter_consumption)
            client.publish("homepro/gas_meter_status", elec_meter_status)

            client.publish("homepro/gas_meter/consumption", gas_meter_consumption)
            client.publish("homepro/gas_meter/status", gas_meter_status)
            client.publish("homepro/gas_meter/info", get_meter_info("gas"))
        except:
            logging.error("Error publishing gas to MQTT")

    time.sleep(5)
