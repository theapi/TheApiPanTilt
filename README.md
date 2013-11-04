Picam
=====

Tools for playing with the Raspberry Pi camera on a pan &amp; tilt mount.

How to setup the pan & tilt is detailed in the
[Dawn Robotics blog](http://blog.dawnrobotics.co.uk/2013/10/using-the-dagu-pantilt-kit-with-the-raspberry-pi/)
```
sudo apt-get install python-dev python-pip
sudo pip install RPIO

```

The browser based joystick comes from
[https://github.com/jeromeetienne/virtualjoystick.js](https://github.com/jeromeetienne/virtualjoystick.js)


Requirements
============
[websocket-client](https://github.com/liris/websocket-client)
```
pip install websocket-client
```

The excellent [SimpleWebSocketServer](https://github.com/opiate/SimpleWebSocketServer)
As this is just one file with no install, I've included in this repo.


To Use
======

 - ws_server.py for the websocket server.
 - joystick.html a joystick websocket client for a browser
 - main.py which controls the servos. It is a websocket client.

ws_server.py can be run on a seperate pi (server) than main.py since
main.py connects via websockets to get its requested vectors.
This also means that main.py, which is run as root, is seperated
from the evils that lurk on the internet.

First start the websocket server:
```
python ws_server.py --host=192.168.0.145
```

Then start the pan &amp; tilt controller
```
sudo python main.py --host=192.168.0.145
```
To invert the pan use the -P flag
```
sudo python main.py --host=192.168.0.145 -P
```
To invert the tilt use the -T flag
```
sudo python main.py --host=192.168.0.145 -T
```

A virtual pan & tilt is availble if pygame is installed.
(sudo apt-get install python-pygame)
Choose the "cube" driver with the -d (--driver) option
```
sudo python main.py --host=192.168.0.145 -T -P --driver=cube
```

(Your host ip address may/will be different)

Then open joystick.html in a browser, preferably via a touch screen.

Touch the screen, and you finger will create a virtual joystick.
Slight movements are all that are required.
The greater the distance the joystick is from where you first touched,
the greater the speed.



