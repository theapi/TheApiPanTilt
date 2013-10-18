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
WebSocket-for-Python - https://github.com/Lawouach/WebSocket-for-Python
```
sudo easy_install ws4py
```

[CherryPy](http://www.cherrypy.org/)

[http://download.cherrypy.org/cherrypy/3.2.2/CherryPy-3.2.2.tar.gz](http://download.cherrypy.org/cherrypy/3.2.2/CherryPy-3.2.2.tar.gz)
```
tar -xvf CherryPy-3.2.2.tar.gz
cd CherryPy-3.2.2
sudo python setup.py install
```

To Use
======
```
sudo python ws_control.py --host=192.168.0.137
```
(Your host ip address may/will be different)

Then point a browser, preferably via a touch screen, to
```
192.168.0.137:9000
```
The pan & tilt follows your finger (mouse).


