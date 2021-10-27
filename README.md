# OBSbox

A platform for adding plugins to OBS, which can be controlled via a simple web interface

## Setup

1. Install Python 3.6
    - Latest Windows installer: [Python 3.6.8](https://www.python.org/downloads/release/python-368/)
2. Install websockets 3.4 with pip
    - `pip install -Iv websockets==3.4`
    - If pip (for Python 3.6) is not in the PATH, use its file path
    - Windows (default install location):
        - Replace `{user}` with your username abbreviation
        - `> C:\Users\{user}\AppData\Local\Programs\Python\Python36\python.exe -m pip install -Iv websockets==3.4`
3. Add the python install path to OBS
    1. Tools > Scripts > Python Settings > Python Install Path (64bit) > Browse
    2. Select the python install folder
        - Windows default install location: `C:/Users/{user}/AppData/Local/Programs/Python/Python36`
4. Add the python script to OBS
    1. Tools > Script > Scripts > + (Add Scripts)
    2. Select OBSbox.py from this directory
5. Accessing the webpage from the device OBS is running on
    - Go to [localhost:8080](http://localhost:8080/)
6. Accessing the webpage from another device on the same network (optional)
    1. Get the host device's IP address (will probably look like 192.168.\*.\*)
        - Windows: `> ipconfig` > IPv4 Address
        - Ubuntu + other GNU/Linux with ifconfig installed: `> ifconfig` > inet
    2. Tools > Scripts > Scripts > OBSbox.py > IP Address: the ip address from the previous step
    3. Restart OBS
    4. Go to `http://{ip address}:8080/` (replacing {ip address with the ip address from step 1}) on another device (on the same network) or the host device

## Adding modules

Simply place the module file in the same folder as OBSbox.py

### Advanced Notes:
- The ports of the webserver and API can be changed from their appropriate options in the script settings
- The ports may need to be opened when using a firewall
- The ports can be port forwarded for access from the wider internet but this is not advised, especially as the webserver is not SSL encrypted