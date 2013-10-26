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
[WebSocket-for-Python](https://github.com/Lawouach/WebSocket-for-Python)
```
sudo easy_install ws4py
```

[gevent](http://www.gevent.org/)
```
sudo apt-get install python-gevent
```

To Use
======

There are two scripts:
 - websocket.py for the websocket server which also provides
a virtual joystick for capable browsers.
 - pan_tilt.py which controls the servos. It is itself a websocket client.

websocket.py can be run on a seperate pi (server) than pan_tilt.py since
pan_tilt.py connects via websockets to get its requested vectors.
This also means that pan_tilt.py, which is run as root, is seperated
from the evils that lurk on the internet.

First start the websocket server:
```
python websocket.py --host=192.168.0.137
```
Then start the pan &amp; tilt controller
```
sudo python pan_tilt.py --host=192.168.0.137
```

(Your host ip address may/will be different)

Then point a browser, preferably via a touch screen, to
```
192.168.0.137:9001
```
Touch the screen, and you finger will create a virtual joystick.
Slight movements are all that are required.
The greater the distance the joystick is from where you first touched,
the greater the speed.



