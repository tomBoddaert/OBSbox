# OBSbox

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