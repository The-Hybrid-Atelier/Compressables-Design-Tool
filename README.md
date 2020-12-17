# Compressables
### Subtitle Here

![Compressables](images/exemplars/compressables.png)

This repository is the official implementation of the X paper [Compressables](TODO:LinkToACM).

## Authors
Anonymized

## Design Tool
* [Online Tool](TODO)
* [Source Code](TODO)

## Getting Started



### Making a Stress Glove
Check out our [Instructable](anonymized) on how to make a stress glove compressable.

### Running the App (Cloud)
Please note that data is not encrypted or protected when using our cloud server. This app is available for development purposes only. You can download and run the app on your local computer (instruction below) to restrict access to your local area network.

Use SERVER_IP = XXX.XXX.XX.XX when configuring your Fruit.ino code below.

To use the app (online), simply point your browser to:
http://www.anonymized.com

### Running the Server (Locally)
On your local machine, download and install ruby-2.6.3 using rvm. 

Install the following gems in your CLI. 
```
gem install em-websocket
```
Run the server:
```
# specify a port  (default: 3001)
rb server.rb -p 3001
>> Server started at ws://<YYY.YYY.YY.YYY>:<PORT>
```
Use the IP address (YYY.YYY.YY.YYY) that is printed in your terminal.
Use SERVER_IP = YYY.YYY.YY.YYY when configuring your Fruit.ino code below.
To use the app (locally), navigate to the rails-app folder.
```
# install packages
bundle install
# run the app
rails s
```
Point your browser to:
http://localhost:3000

 
### Configuring your Hardware
Configuring the Programmable Air: Upload the PA.ino code to your ProgrammableAir using the Arduino IDE. 
Upload the Fruit.ino code onto an Adafruit WiFi Feather (WINC5000). Be sure to update the WIFI_SSID and WIFI_PASS in arduino_secrets.h. Also, update the SERVER_IP address of the websocket server. 
Wire the Programmable Air to the Feather following the [Wiring Schematic](TODO). 

### Hello World
Open http://localhost:3000/iot/air or anonymized_link
Input the IP address of the server
Connect
Start sending commands to your Programmable Air. Open the Log to see the command syntax. 
### Hello World (Program)
Run the hello_world.py program. 
Alter the ws.send messages with commands from the app Log.
 

## Contributing
The material available through this repository is open-source under the MIT License. 
We welcome contributions of community-made designs! You can either submit a pull request via Github or send us a link to your Instructables, Thingiverse, or design files to anonymized.


