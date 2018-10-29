
import pdb
import argparse
import socket
from collections import deque
from hashlib import sha256

class TaskQueueServer:

    def __init__(self, ip, port, path, timeout):
        print(ip, "==>", port)
        self.path = path
        self.timeout = timeout
        self.queue = Queues()
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(2)

    def run(self):
        while True:
            (conn, address) = self.socket.accept()
            handler = Handler(conn, address, self.queue)
            handler.handle()

    def __del__(self):
        self.socket.close()


class Handler:
    def __init__(self, connection, address, queue):
        self.address = address
        self.socket = connection
        self.queue = queue
    
    def handle(self):
        data = self.socket.recv(1024).decode().strip()
        print(data)
        command, args = data.split(' ', 1)
        response = self.proccess(command, args)
        print("response = ", response)
        print("End connection to {}".format(self.address))
        self.socket.send(response.encode())
        self.socket.close()
    
    def proccess(self, act, args):
        print(act)
        commands = {
            'GET': self.queue.get,
            'ACK': self.queue.ack,
            'ADD': self.queue.add,
            'IN': self.queue.check_in,
            'SAVE': self.queue.save
        }
        try:
            response = commands[act](args.split())
            return response
        except Exception as e:
            print(e)
            return "ERROR"


class Queues:
    def __init__(self):
        self.queues = {}
        self.len = 0
    
    def get(self, args):
        name = args
        if name not in self.queues or not len(self.queues[name]):
            return None
        task = self.queues[name].popleft()
        return str(task)
    
    def add(self, args):
        print('args = ', args)
        queue, length, data = args
        task = Task(length, data)
        if queue not in self.queues:
            self.queues[queue] = deque()
        self.queues[queue].append(task)
        return task.id

    
    def ack(self, args):
        pass
    
    def check_in(self, args):
        pass
    
    def save(self, args):
        pass


class Task:
    def __init__(self, length, data):
        self.length = length
        self.data = data
        self.status = 0
        self.id = self.get_id()
    
    def get_id(self):
        global number
        number += 1
        return sha256(str(number).encode()).hexdigest()
    
    def __str__(self):
        return "{} {} {}".format(self.id, self.length, self.data)
    

def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=8080,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


number = 0

if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
