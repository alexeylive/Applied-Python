import uuid
import re
import argparse
import datetime
import socket
import collections
import pickle
import os


class Task:
    def __init__(self, data='', length=0):
        self.data = data
        self.length = length
        self.id = str(uuid.uuid4())
        self.underway = False


class TaskQueues:
    def __init__(self):
        self.queues = collections.defaultdict(collections.deque)
        self.in_progress = collections.defaultdict(list)

    def add_task(self, match):
        if int(match.group('length')) > 10 ** 6 or int(match.group('length')) != len(match.group('data')):
            return 'ERROR'

        task = Task(match.group('data'), int(match.group('length')))
        self.queues[match.group('queue')].append(task)
        return task.id

    def get_task(self, match):
        for task in self.queues[match.group('queue')]:
            if not task.underway:
                task.underway = True
                task.receiving = datetime.datetime.now()
                self.in_progress[match.group('queue')].append(task)
                return '{} {} {}'.format(task.id, task.length, task.data)
        return None

    def ack_task(self, match):
        for task in self.queues[match.group('queue')]:
            if task.id == match.group('id'):
                self.queues[match.group('queue')].remove(task)
                if task.underway:
                    self.in_progress[match.group('queue')].remove(task)
                return 'YES'
        return 'NO'

    def exist_task(self, match):
        for task in self.queues[match.group('queue')]:
            if task.id == match.group('id'):
                return 'YES'
        return 'NO'

    def check_timeout(self, timeout):
        to_delete = []
        for queue in self.in_progress.values():
            to_delete.clear()
            for ind, task in enumerate(queue):
                if datetime.datetime.now() - task.receiving > timeout:
                    task.receiving = 0
                    task.underway = False
                    to_delete.append(ind)
                else:
                    break
            for ind in reversed(to_delete):
                del queue[ind]


class Server:

    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.timeout = datetime.timedelta(seconds=timeout)
        self.path = os.getcwd() + path
        self.available_cmd = ['add', 'save', 'ack', 'in', 'get']
        if os.path.exists(self.path):
            self.queues = pickle.load(open(self.path, 'rb'))['queues']
        else:
            self.queues = TaskQueues()

    def execution(self, command):
        name, *args = command.split(' ')
        if not name:
            return 'ERROR'

        name = name.strip().lower()
        if name not in self.available_cmd:
            return 'ERROR'

        cmd, match = self.preparation(name, command)
        if not match:
            return 'ERROR'

        return cmd(match)

    def preparation(self, name_cmd, cmd):
        if name_cmd == 'save':
            return self.save, 'save'

        elif name_cmd == 'add':
            pattern = re.compile('(?P<method>.*) (?P<queue>.*) (?P<length>.*) (?P<data>.*)')
            command = self.queues.add_task
        elif name_cmd == 'get':
            pattern = re.compile('(?P<method>.*) (?P<queue>.*)')
            command = self.queues.get_task
        elif name_cmd == 'ack' or name_cmd == 'in':
            pattern = re.compile('(?P<method>.*) (?P<queue>.*) (?P<id>.*)')
            if name_cmd == 'ack':
                command = self.queues.ack_task
            else:
                command = self.queues.exist_task
        return command, pattern.match(cmd.rstrip())

    def save(self, match):
        to_save = {'queues': self.queues}
        pickle.dump(to_save, open(self.path, 'wb'))
        return 'OK'

    def response(self, conn, resp):
        conn.send(resp.encode('utf'))
        conn.shutdown(1)
        conn.close()

    def run(self):
        print('Starting the server...')
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind((self.ip, self.port))
        print('Server is waiting for connection')
        connection.listen(1)
        while True:
            try:
                current_conn, addr = connection.accept()
                command = current_conn.recv(1048576).decode('utf')
                self.queues.check_timeout(self.timeout)
                resp = self.execution(command)
                self.response(current_conn, resp)

            except KeyboardInterrupt:
                print('Shutting down...')
                connection.close()
                break
        print('Server off')


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
        default='/cash',
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
    args = parse_args()
    server = Server(**args.__dict__)
    server.run()
