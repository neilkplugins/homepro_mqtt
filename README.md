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

This latest version looks for a  configuration file in the same directory of the script `mqtt_publisher_config` called `mqtt.cfg`

A sample `mqtt.cfg` file is in the repository and should be stored in `/root/mqtt/mqtt.cfg`

This version will read the broker IP and port from this file, a sample is in the repository.  If you are not using a password then you can delete the authentication section.

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

check if your broker is recieving messages in your favourite tool (I use MQTT explorer), and look for any errors in mqtt.log


* Finally power cycle your home pro (entirely at your own risk, the only recovery at present if this fails is a hard reset, and your container will be wiped back to default)*


At present the script still publishes updates even the home pro is in the dreaded flashing CAD state, I may enhance this to check and skip publishing in that circumstance, and alternate thought will be this will show the duration of any meter dropouts so both approaches may be beneficial depending on what you do with the data afterwards.

### This Latest Version with Authentication Support has more robust error checking so API failures do not throw exceptions and kill the script

I haven't tested it for too long but this version seems much more resilient with all api calls and processing wrapped in a `try / except` block

## "Warning about the V1 Call back deprecation"

You will get a warning message from the script that the V1 callback API will be deprecated.  This will work fine, however I have a test version that uses the V2 API that avoids the warning, it is the file `mqtt_publisher_nowarning.py` which I am testing more before merging into the main release.  Feel free to try it.

## Old Startup approach - Method Create a shell script in the root directory to act as a wrapper in startup.sh

This shouldn't be needed anymore, but kept the details in case anyone was using it.

`nano start_mqtt.sh`

Insert the following
```
#!/bin/bash
/usr/bin/python3 /root/mqtt/mqtt_publisher.py &
```
make the script executable

`chmod +x start_mqtt.sh`

test it by running it

`./start_mqtt.sh`

### If all is good, edit your startup.sh so it looks like this

```
#!/bin/bash

# Ensure our main env shows up in ssh sessions
# we're passing on API host info
env | grep _ >> /etc/environment
# Start mqtt_publisher
/root/start_mqtt.sh
# Start the ssh server
/usr/sbin/sshd -D
```



