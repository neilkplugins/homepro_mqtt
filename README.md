# homepro_mqtt
MQTT script for the Home Pro provided on an entirely "as is" basis, use entirely at your own risk.  More than happy for others to contribute, and I am learning as I go.

Basic Instructions

SSH into your home pro

Install paho

pip3 install paho-mqtt

Create the mqtt directory

mkdir mqtt
cd mqtt
nano mqtt_publisher.py

Paste in the code from the repository (edit in the correct address for your broker)

Test it by running python3 mqtt_publisher.py

Use your preferred tool to check if the topics are posted to your broker

check out mqtt.log in the mqtt folder to see if any errors or posted or if it is publishing messages succesfully.

More later on automating the startup of this when I manage to do it without breaking the home pro and requiring a hard reset.

Will format this page properly when I remeber the tags.
