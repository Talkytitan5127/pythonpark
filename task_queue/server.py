import argparse
import os
import socket
import time
import json
from collections import deque
from hashlib import sha256

class TaskQueueServer:
    def __init__(self, ip, port, path, timeout):
        self.queue = Queues(timeout, path)
        proc_file = path+'process.log'
        que_file = path+'queue.log'
        if os.path.exists(proc_file) and os.path.exists(que_file):
            self.queue.load()
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def run(self):
        while True:
            self.queue.check_time()
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
        data = self.socket.recv(10**6+1).decode().strip()
        response = self.proccess(data)
        self.socket.send(response.encode())
        self.socket.close()
    
    def proccess(self, data):
        data = data.split()
        act = data.pop(0)
        commands = {
            'GET': self.queue.get,
            'ACK': self.queue.ack,
            'ADD': self.queue.add,
            'IN': self.queue.check_in,
            'SAVE': self.queue.save,
        }
        try:
            response = commands[act](*data)
            return response
        except Exception:
            return "ERROR"


class Queues:
    def __init__(self, timeout, path):
        self.path = path
        self.queues = {}
        self.que_process = {}
        self.proc_count = 0
        self.timeout = timeout
    
    def get(self, name):
        if name not in self.queues or not len(self.queues[name]):
            return "NONE"
        task = self.queues[name].popleft()
        task.prepare(self.proc_count)
        self.que_process[name][task.id] = task
        self.proc_count += 1
        return str(task)
    
    def add(self, queue, length, data):
        task = Task(length, data)
        if queue not in self.queues:
            self.queues[queue] = deque()
            self.que_process[queue] = dict()
        self.queues[queue].append(task)
        return task.id
    
    def ack(self, name, task_id):
        if task_id not in self.que_process[name].keys():
            return "NO"
        del self.que_process[name][task_id]
        self.update_proc(name)
        return "YES"
        
    def update_proc(self, name):
        self.proc_count = 0
        new_proc = dict()
        for key, value in sorted(self.que_process[name].items(), key=lambda elem: elem[1].pos):
            value.pos = self.proc_count
            new_proc[key] = value
            self.proc_count += 1
        self.que_process[name] = new_proc
        
    def check_in(self, name, task_id):
        if not name in self.queues:
            return "NO"
        if task_id in [elem.id for elem in self.queues[name]] \
            or \
            task_id in self.que_process[name].keys():
            return "YES"
        return "NO"
    
    def check_time(self):
        delete = []
        for ques in self.que_process.keys():
            if not len(self.que_process[ques]):
                continue
            for key, task in sorted(self.que_process[ques].items(), key= lambda elem: elem[1].pos):
                if int(time.time() - task.time) >= self.timeout:
                    delete.append((ques,key))
        if not delete:
            return
        for elem in delete:
            que, key = elem
            task = self.que_process[que].pop(key)
            self.queues[que].insert(int(task.pos), task)

    def save(self):
        save = {}
        for key in self.queues:
            save[key] = [elem.tjson() for elem in self.queues[key]]
        with open(self.path+"queue.log", 'w') as que_file:
            print(json.dumps(save), file=que_file) 
        save = {}
        for key in self.que_process:
            save[key] = dict()
            for elem, task in self.que_process[key].items():
                save[key][elem] = task.tjson()
        with open(self.path+"process.log", 'w') as proc_file:
            print(json.dumps(save), file=proc_file) 
        
        return "OK"
    
    def load(self):
        que_file = self.path+'queue.log'
        proc_file = self.path+'process.log'
        data = None
        que = {}
        with open(que_file, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                que[key] = deque([Task(**elem) for elem in value])
        self.queues = que
        proc = {}
        with open(proc_file, 'r') as f:
            data = json.load(f)
            for name in data.keys():
                proc[name] = {}
                for key, task in data[name].items():
                    proc[name][key] = Task(**task)
        self.que_process = proc
        os.remove(que_file)
        os.remove(proc_file)
        return "OK"



class Task:
    def __init__(self, length, data, time=0, pos=-1, id=0):
        self.length = length
        self.data = data
        self.time = time
        self.id = id or self.get_id()
        self.pos = pos
    
    def get_id(self):
        global number
        number += 1
        return str(number)
    
    def prepare(self, pos):
        self.pos = pos
        self.time = time.time()
    
    def __str__(self):
        return "{} {} {}".format(self.id, self.length, self.data)
    
    def tjson(self):
        return {
            'length': self.length,
            'data': self.data,
            'time': self.time,
            'id': self.id,
            'pos': self.id
        }

def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
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


if __name__ == '__main__':
    number = 0
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
