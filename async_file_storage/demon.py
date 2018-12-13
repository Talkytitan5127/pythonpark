import argparse
import concurrent.futures
from os.path import isfile
import yaml
from aiohttp import web, ClientSession

class Handler:
    def __init__(self):
        self.path = config['directory']

    async def get_file(self, request):
        print("Handler")
        filename = request.match_info['filename']
        fh = FileManager(self.path, filename)
        data = fh.getter()
        if data is None:
            if request.rel_url.query:
                return web.HTTPNotFound(text="file doesn't exist")
            
            asker = Asker(filename)
            data = await asker.getter()
            if data is None:
                return web.HTTPNotFound(text="file doesn't exist")
            if config['save']:
                fh.setter(data)
            return web.json_response(data)
        
        return web.json_response({'filename': filename, 'text': data})


class Asker:
    def __init__(self, filename):
        self.demons = config['demons']
        self.filename = filename
    
    async def getter(self):
        print("getter")
        result = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_url = {executor.submit(self.ask_demon, demon): demon for demon in self.demons}
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                resp = await data
                result.append(resp)
        
        for resp in result:
            if resp.status == 200:
                data = await resp.json()
                return data
        
        return None
    
    async def ask_demon(self, demon):
        req_form = "http://{}:{}/{}".format(demon['host'], demon['port'], self.filename)
        params={'demon': 'true'}
        async with ClientSession() as session:
            async with session.get(req_form, params=params) as resp:
                return resp


class FileManager:
    def __init__(self, directory, filename):
        self.filename = directory + '/' + filename

    def getter(self):
        if not isfile(self.filename):
            return None
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        proc = executor.submit(get_content, self.filename)
        data = proc.result()
        return data
    
    def setter(self, data):
        data['filename'] = self.filename
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        proc = executor.submit(write_content, data)
        proc.result()
        return


def get_content(filename):
    print('get_content')
    with open(filename, 'r') as f:
        mas = [string for string in f]
    return ''.join(mas)

def write_content(data):
    print("write_content")
    with open(data['filename'], 'w') as f:
        print(data['text'], file=f)
    
    return

def parse_args():
    parser = argparse.ArgumentParser(description='Async demons.')
    parser.add_argument('--file', help='yaml-file config', dest='filename')
    return parser.parse_args()

def get_config(filename):
    data = None
    try:
        with open(filename, 'r') as f:
            data = yaml.load(f)
    except FileNotFoundError:
        return None    
    return data

def set_app():
    handler = Handler()

    app = web.Application()
    app.router.add_routes(
        [web.get('/{filename}', handler.get_file)]
    )

    return app


parser = parse_args()
config = get_config(parser.filename)
if config is None:
    print('config file doesn\'t exists')
    exit(1)
app = set_app()
web.run_app(app, port=config['port'])

