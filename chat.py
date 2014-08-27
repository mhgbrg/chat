__author__ = 'mats'


import zmq
import sys
from multiprocessing import Process

topics = []
# [{'name': 'chalmers', 'type': 'send'}, {'name': 'chalmers', 'type': 'receive'}]

receivers = []
# ['localhost:8888', 'localhost:8889', 'localhost:8890']

processes = []
# [
#   {'process': <process>, 'address': 'localhost:8888', 'topic': 'chalmers'},
#   {'process': <process>, 'address': 'localhost:8888', 'topic': 'avancez'}
# ]


def start_chat(args):
    topic_name = args[3]
    topics.append({'name': topic_name, 'type': 'send'})
    topics.append({'name': topic_name, 'type': 'receive'})

    port = args[1]
    nickname = args[2]
    send(port, nickname)


def send(port, nickname):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    while True:
        msg = raw_input()

        if msg[0] != '/':
            send_message(socket, msg, nickname)
        else:
            args = msg.split(' ')

            if args[0] == '/exit':
                break
            elif len(args) == 1:
                display_help(args[0][1:])
            else:
                arg1 = args[1]
                if args[0] == '/connect':
                    connect(arg1)

                elif args[0] == '/disconnect':
                    disconnect(arg1)

                elif args[0] == '/add_topic':
                    if len(args) < 3:
                        display_help(args[0])
                    else:
                        add_topic(args[2], args[1])

                elif args[0] == '/remove_topic':
                    if len(args) < 3:
                        display_help(args[0])
                    else:
                        remove_topic(args[2], args[1])

                elif args[0] == '/help':
                    display_help(arg1)

                else:
                    display_help('/help')


def start_process(address, topic_name):
    process = Process(target=receive, args=(address, topic_name))
    process.daemon = True
    process.start()
    processes.append({'process': process, 'address': address, 'topic': topic_name})


def terminate_process(i):
    processes[i]['process'].terminate()
    del processes[i]


def start_processes_for_address(address):
    for topic in topics:
        if topic['type'] == 'receive':
            start_process(address, topic['name'])


def terminate_processes_for_address(address):
    for i, process in enumerate(processes):
        if process['address'] == address:
            terminate_process(i)


def start_processes_for_topic(topic_name):
    for address in receivers:
        start_process(address, topic_name)


def terminate_processes_for_topic(topic_name):
    for i, process in enumerate(processes):
        if process['topic'] == topic_name:
            terminate_process(i)


def connect(address):
    if address not in receivers:
        receivers.append(address)
        start_processes_for_address(address)
        print 'connected to %s' % address
    else:
        print 'already connected to %s' % address


def disconnect(address):
    if address in receivers:
        terminate_processes_for_address(address)
        print 'disconnected from %s' % address
    else:
        print 'not connected to %s' % address


def add_topic(name, type):
    if type not in ('send', 'receive'):
        display_help('/topic')
    else:
        topic_found = check_for_topic(name, type)

        if not topic_found:
            topics.append({'name': name, 'type': type})

            if type == 'receive':
                start_processes_for_topic(name)
        else:
            if type == 'send':
                print 'already sending to topic %s' % name
            elif type == 'receive':
                print 'already receiving from topic %s' % name


def remove_topic(name, type):
    if type not in ('send', 'receive'):
        display_help('/topic')
    else:
        topic_found = check_for_topic(name, type)

        if topic_found:
            for i, topic in enumerate(topics):
                if topic['name'] == name and topic['type'] == type:
                    topics.pop(i)

            if type == 'receive':
                terminate_processes_for_topic(name)
        else:
            if type == 'send':
                print 'not sending to topic %s' % name
            elif type == 'receive':
                print 'not receiving from topic %s' % name


def check_for_topic(name, type):
    topic_found = False
    for topic in topics:
        if topic['name'] == name and type == topic['type']:
            topic_found = True
            break
    return topic_found


def send_message(socket, msg, nickname):
    for topic in topics:
        if topic['type'] == 'send':
            socket.send('%s %s: %s' % ('#' + topic['name'], '<' + nickname + '>', msg))


def receive(address, topic_name):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.connect("tcp://%s" % address)
    socket.setsockopt(zmq.SUBSCRIBE, '#' + topic_name)

    while True:
        msg = socket.recv()
        print msg


def display_help(command):
    if command == 'connect':
        print '/connect - connect to another user\n'

        print 'Usage:'
        print '/connect <ip:port>'
        print 'Example: /connect 192.168.1.2:8888'
    elif command == 'disconnect':
        print '/disconnect - disconnect from a connected user\n'

        print 'Usage:'
        print '/disconnect <ip:port>'
        print 'Example: /disconnect 192.168.1.2:8888'
    elif command == 'add_topic':
        print '/add_topic - add topic\n'

        print 'Usage:'
        print '/add_topic <send/receive> <topic>'
        print 'Example: /add_topic send chalmers'
        print 'Example: /add_topic receive avancez'
    elif command == 'remove_topic':
        print '/remove_topic - add topic\n'

        print 'Usage:'
        print '/remove_topic <send/receive> <topic>'
        print 'Example: /remove_topic send chalmers'
        print 'Example: /remove_topic receive avancez'
    else:
        print 'Valid commands:\n'

        print '/help - display this information'
        print '/connect - connect to another user'
        print '/disconnect - disconnect from a connected user'
        print '/add_topic - add topic'
        print '/remove_topic - remove topic\n'

        print 'For more information about a specific command, use /help <command>'


if __name__ == '__main__':
    start_chat(sys.argv)