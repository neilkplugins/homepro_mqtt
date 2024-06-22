# homepro_mqtt
MQTT script for the Home Pro provided on an entirely "as is" basis, use entirely at your own risk.  More than happy for others to contribute, and I am learning as I go.

Basic Instructions

### SSH into your home pro

`ssh -p 8023 -o HostKeyAlgorithms=+ssh-rsa root@<home_pro_ip>`

### Install paho

`pip3 install paho-mqtt`

### Create the mqtt directory

```
mkdir mqtt
cd mqtt
nano mqtt_publisher.py
```

Create the Script

Paste in the code from the repository 

### Create the config file

```
[broker]
ip=192.168.1.41
port=1883
[authentication]
username=temp
password=temp
[meters]
electricity=True
gas=True
[logging]
level=INFO
```

This latest version looks for a  configuration file in the same directory of the script `mqtt_publisher_config` called `mqtt.cfg`

A sample `mqtt.cfg` file is in the repository (and above) and should be stored in `/root/mqtt/mqtt.cfg`

This version will read the broker IP and port from this file, a sample is in the repository.  If you are not using a password then you can delete the authentication section.

You can also configure if you wish to publish Gas and Electricty meter messages by setting the appropriate entry to `True` or `False`

Logging now defaults to `ERROR` level, add the logging entry and set to `INFO` for more verbose logging.  You can change this to `ERROR` once everything is running fine and to avoid large log files.

Update this with your broker address and port, and if you do not require a password for your broker remove/do not copy the `[authentication]` section

### Authentication support

If you add an `[authentication]` section and add entries to the `mqtt.cfg` file, it will use the password and username for the broker connection.


### If you are done Test it by running 

`python3 mqtt_publisher.py`

Use your preferred tool to check if the topics are posted to your broker

check out `mqtt.log` in the mqtt folder to see if any errors or posted or if it is publishing messages succesfully.

### Make it Start automagically (but with the risk you may need a full reset and wipe your container if something goes wrong !!)
### Proceed only if you accept the risk of becoming even more familiar with the hard reset process !!

Edit the startup.sh and add the following line

`nohup python3 /root/mqtt/mqtt_publisher.py >/dev/null 2>&1 &`

Just after the grep statement

check if your broker is recieving messages in your favourite tool (I use MQTT explorer), and look for any errors in mqtt.log (you may need to set the logging level to `INFO` in the mqtt.cfg file if you are not seeing messages published.


* Finally power cycle your home pro (entirely at your own risk, the only recovery at present if this fails is a hard reset, and your container will be wiped back to default)*


At present the script still publishes updates even the home pro is in the dreaded flashing CAD state, I may enhance this to check and skip publishing in that circumstance, and alternate thought will be this will show the duration of any meter dropouts so both approaches may be beneficial depending on what you do with the data afterwards.

### This Latest Version with Authentication Support has more robust error checking so API failures do not throw exceptions and kill the script

I haven't tested it for too long but this version seems much more resilient with all api calls and processing wrapped in a `try / except` block

## "Warning about the V1 Call back deprecation"

You may get a warning message from the script that the V1 callback API will be deprecated with earlier versions, this is now adressed

Thanks also to MuddyRock for the contribution (and suggestion on the logging)

