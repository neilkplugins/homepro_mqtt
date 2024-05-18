import os
import requests
import paho.mqtt.client as mqtt
import logging
import time
from datetime import datetime

# Add and setup logging to a file in /root/mqtt which is also where  I  store the  script
logging.basicConfig(filename='/root/mqtt/mqtt.log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.INFO)

logging.info("Running MQTT Publisher")

logger = logging.getLogger('MQTT')
# Other definitions including your broker address
han_host = os.getenv('HAN_API_HOST')
broker="192.168.1.41"
port=1883
# Create a flag in class to track MQTT broker connection success
mqtt.Client.connected_flag=False

def on_publish(client , userdata, mid):             #create function for callback
	logger.info("MQTT topic published")
	pass
def on_connect(client, userdata, flags, rc):
	if rc==0:
		logger.info("Connected to MQTT Broker  Returned code="+str(rc))
		client.connected_flag = True
	else:
		logger.info("Bad connection to MQTT BrokerReturned code="+str(rc))
def on_disconnect(client, userdata, rc):
	logger.info("Disconnected from MQTT broker  "+str(rc))
	client.connected_flag = False

#   start the client and define callbacks
client=mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
logger.info("Connecting to Broker "+broker)
# Run the main loop
client.loop_start()
try:
	client.connect(broker, 1883, 60)
except:
	logger.info("Connection to "+broker+" failed")
while not client.connected_flag: #wait in loop
	logger.info("Waiting for Broker connection")
	time.sleep(1)
logger.info("Started Main Loop")
while True:
	#Check broker connection and wait for reconnect
	if client.connected_flag:
		pass
	else:
		while not client.connected_flag: #wait in loop
			logger.info("Waiting for Broker connection")
			time.sleep(5)
	# set timestamp for this update loop
	current_timestamp = str(datetime.utcnow())
	logger.info("Update cycle started "+current_timestamp)
	# Get elec meter consumption
	consump_response = requests.post(han_host + "/get_meter_consumption", json={"meter_type": "elec"})
	if consump_response.ok:
		elec_meter_consumption = consump_response.json()["meter_consump"]
		logger.info("Electricity Consumption returned")
		#print("Meter consumption for {} meter: {}".format("elec", elec_meter_consumption))
	else:
		logger.info("Error calling get_meter_consumption API: {}".format(consump_response.json()["Status"]))
	# Get elec meter status
	status_response = requests.post(han_host + "/get_meter_status", json={"meter_type": "elec"})
	if status_response.ok:
		elec_meter_status = status_response.json()["meter_status"]
		logger.info("Electricity Meter Status returned")
		#print("Meter status for {} meter: {}".format("elec", elec_meter_status))
	else:
		logger.info("Error calling get_meter_status API: {}".format(elec_meter_status_response.json()["Status"]))
	# Get gas  meter consumption
	gas_consump_response = requests.post(han_host + "/get_meter_consumption", json={"meter_type": "gas"})
	if gas_consump_response.ok:
		gas_meter_consumption = gas_consump_response.json()["meter_consump"]
		logger.info("Gas Consumption returned")
		#print("Meter consumption for {} meter: {}".format("gas", gas_meter_consumption))
	else:
		logger.info("Error calling get_meter_consumption API: {}".format(gas_consump_response.json()["Status"]))
	# Get gas meter status
	gas_status_response = requests.post(han_host + "/get_meter_status", json={"meter_type": "gas"})
	if gas_status_response.ok:
		gas_meter_status = gas_status_response.json()["meter_status"]
		logger.info("Gas Meter Status returned")
		#print("Meter status for {} meter: {}".format("gas", gas_meter_status))
	else:
		logger.info("Error calling get_meter_status API: {}".format(gas_meter_status_response.json()["Status"]))

	#Publish to  MQTT Broker
	ret= client.publish("homepro/elec_meter",elec_meter_consumption)
	ret2 = client.publish("homepro/elect_meter_status", elec_meter_status)
	ret3 = client.publish("homepro/gas_meter", gas_meter_consumption)
	ret4 = client.publish("homepro/gas_meter_status", gas_meter_status)
	time.sleep(5)
