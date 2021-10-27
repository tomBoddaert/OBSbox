print('OBSbox starting...')

debug = False

from concurrent.futures import thread
import os, asyncio, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import websockets

try:
    import obspython as obs
except ImportError:
    pass

# --- Module setup ---

def is_valid_module(pythonFile):
    if not hasattr(pythonFile, 'Main'):
        return False

    module = pythonFile.Main
    return hasattr(module, '__init__') and hasattr(module, 'name') and hasattr(module, 'inputs') and hasattr(module, 'instances') and hasattr(module, 'destroy')

moduleFiles = os.listdir(os.path.dirname(os.path.abspath(__file__)))
pythonFiles = [__import__(moduleFile[:-3]) for moduleFile in moduleFiles if moduleFile.endswith('.py') and moduleFile != 'OBSbox.py']
modules = [pythonFile.Main for pythonFile in pythonFiles if is_valid_module(pythonFile)]

if debug: print('OBSbox modules imported')

# --- OBS setup ---

def script_description():
    return 'OBSbox\n  Add plugins to OBS with a web interface'

def script_tick(dt):
    for module in modules:
        if hasattr(module, 'tick'):
            for instance in module.instances.values():
                instance.tick(dt)

# --- Web interface ---

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'r') as file:
    homepage = file.read()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):

        response = self._render_page()
        self.send_response(response['code'])
        self.send_header('Content-type', response['type'])
        self.end_headers()

        self.wfile.write(bytes(response['text'], 'utf8'))

    def do_POST(self):
        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)

        # self.send_response(200)
        # self.end_headers()

        # response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        # response.write(body)
        # self.wfile.write(response.getvalue())
        self.send_response(404)
        self.wfile.write(bytes('', 'utf8'))

    def log_message(self, format: str, *args) -> None:
        if debug: return super().log_message(format, *args)

    def _render_page(self):
        if self.path == '/':
            return {
                'code': 200,
                'type': 'text/html',
                'text': render_homepage()
            }

        return {
            'code': 404,
            'type': 'text/html',
            'text': ''
        }

def render_homepage():
    if not debug:
        return homepage

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'r') as file:
        return file.read()

if debug: print('OBSbox webpage setup')

# --- WebSocket API ---

saveQueued = False

def get_module_data():
    return {
        'type': 'moduleData',
        'data': [{'module': module.name, 'description': hasattr(module, 'description') and module.description, 'inputs': module.inputs, 'instances': {instNo: instance.data for instNo, instance in module.instances.items()}} for module in modules]
    }

async def broadcast_update(data):
    dataStr = json.dumps(data)
    if debug: print('Sending data')
    for websocket in connected:
        await websocket.send(dataStr)
        if debug: print('.. sent data')

async def handle_API_request(request):
    global saveQueued
    if debug: print(request)
    if not 'cmd' in request:
        return {
            'success': False,
            'error': 'noCmd'
        }

    if request['cmd'] == 'getData':
        return get_module_data()

    if request['cmd'] == 'setInput':
        '''
        {
            "cmd: "setInput",
            "data": {
                "module: *string*,
                "instNo": *int*,
                "input": *string*,
                "value": *bool | float | int | string*
            }
        }
        '''
        module = next(filter(lambda module: module.name == request['data']['module'], modules))
        if not module:
            raise KeyError

        module.instances[request['data']['instNo']].data[request['data']['input']] = request['data']['value']
        if hasattr(module, 'update'):
            module.instances[request['data']['instNo']].update(request['data']['input'])
        await broadcast_update({
            'type': 'input',
            'data': request['data']
        })

        if not saveQueued:
            saveQueued = True
            saveThread.start()

        return None

    if request['cmd'] == 'createInstance':
        '''
        {
            "cmd: "createInstance",
            "data": {
                "module: *string*,
                "inputs": {
                    [*string*]: *bool | float | int | string*
                }
            }
        }
        '''
        module = next(filter(lambda module: module.name == request['data']['module'], modules))
        if not module:
            raise KeyError

        newInst = module(request['data']['inputs'])
        await broadcast_update({
            'type': 'createdInstance',
            'data': {
                'module': request['data']['module'],
                'instNo': newInst.instNo,
                'instData': newInst.data
            }
        })

        if not saveQueued:
            saveQueued = True
            saveThread.start()

        return None

    if request['cmd'] == 'destroyInstance':
        '''
        {
            "cmd: "destroyInstance",
            "data": {
                "module: *string*,
                "instNo": *int*
            }
        }
        '''
        module = next(filter(lambda module: module.name == request['data']['module'], modules))
        if not module:
            raise KeyError

        module.instances[request['data']['instNo']].destroy()
        await broadcast_update({
            'type': 'removedInstance',
            'data': request['data']
        })

        if not saveQueued:
            saveQueued = True
            saveThread.start()

        return None

    return {
        'success': False,
        'error': 'invdCmd'
    }


connected = set()

async def ws_api(websocket: websockets.WebSocketServerProtocol, path):
    global connected

    connected.add(websocket)
    try:
        while True:
            try:
                message = await websocket.recv()
                request = json.loads(message)
                response = await handle_API_request(request)
                if response:
                    await websocket.send(json.dumps(response))

            except (json.JSONDecodeError, KeyError):
                pass
    except (websockets.exceptions.ConnectionClosed, ConnectionResetError, ConnectionAbortedError) as e:
        connected.remove(websocket)
        if debug: print(e)

def startup():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'r') as file:
            data = json.load(file)
            for moduleName, instances in data.items():
                for instance in instances:
                    module = next(filter(lambda module: module.name == moduleName, modules))
                    module(instance)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

threading.Timer(2.0, startup).start()

def save():
    global saveThread, saveQueued
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w') as file:
        json.dump({module.name: [inst.data for inst in module.instances.values()] for module in modules}, file)
    saveThread = threading.Timer(5.0, save)
    saveQueued = False

saveThread = threading.Timer(5.0, save)

if debug: print('OBSbox API setup')

# --- Servers ---

server_ip = '192.168.1.15'
server_address = (server_ip, 8080)
api_address = (server_ip, 8081)

def start_API():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    start_server = websockets.serve(ws_api, api_address[0], api_address[1])
    if debug: print('Starting API at', api_address)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def start_webserver():
    server = HTTPServer(server_address, handler)
    if debug: print('Starting a server at', server_address)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()

APIthread = threading.Thread(target = start_API)
APIthread.daemon = True
APIthread.start()

if __name__ == '__main__':
    start_webserver()
else:
    webserverThread = threading.Thread(target = start_webserver)
    webserverThread.daemon = True
    webserverThread.start()