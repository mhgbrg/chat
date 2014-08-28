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
    if len(args) >= 3 and args[1].isdigit():
        port = args[1]
        nickname = args[2]
    else:
        print 'Error: You must specify port and nickname.'
        print 'Example: chat.py 1337 William'
        return

    if len(args) >= 4:
        topic_name = args[3]
        topics.append({'name': topic_name, 'type': 'send'})
        topics.append({'name': topic_name, 'type': 'receive'})

    send(port, nickname)


def send(port, nickname):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    while True:
        msg = raw_input()

        if msg == '':
            pass
        elif msg[0] != '/':
            send_message(socket, msg, nickname)
        else:
            args = msg.split(' ')
            command = args[0][1:]

            if command == 'exit':
                break
            else:
                if command == 'connect':
                    if len(args) < 1:
                        display_help(command)
                    else:
                        connect(args[1])

                elif command == 'disconnect':
                    if len(args) < 1:
                        display_help(command)
                    else:
                        disconnect(args[1])

                elif command == 'add_topic':
                    if len(args) < 3:
                        display_help(command)
                    else:
                        add_topic(args[2], args[1])

                elif command == 'remove_topic':
                    if len(args) < 3:
                        display_help(command)
                    else:
                        remove_topic(args[2], args[1])

                elif command == 'list_topics':
                    list_topics()

                elif command == 'list_receivers':
                    list_receivers()

                elif command == 'list_processes':
                    list_processes()

                elif command == 'help':
                    if len(args) < 2:
                        display_help()
                    else:
                        display_help(args[1])

                else:
                    display_help()


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


def list_topics():
    sending_topics = []
    receiving_topics = []

    for topic in topics:
        if topic['type'] == 'send':
            sending_topics.append(topic['name'])
        elif topic['type'] == 'receive':
            receiving_topics.append(topic['name'])

    if sending_topics:
        print 'Sending to topics: %s' % ', '.join(sending_topics)
    else:
        print 'Not sending to any topics.'

    if receiving_topics:
        print 'Receiving from topics: %s' % ', '.join(receiving_topics)
    else:
        print 'Not receiving from any topics.'


def list_receivers():
    if receivers:
        print 'Connected to: %s' % ', '.join(receivers)
    else:
        print 'Not connected to any receivers.'


def list_processes():
    if processes:
        pretty_processes = []
        for process in processes:
            pretty_processes.append(process['address'] + ' #' + process['topic'])
        print 'Active processes: %s' % ', '.join(pretty_processes)
    else:
        print 'No active processes.'


def display_help(command=''):
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
    elif command == 'list_topics':
        print '/list_topics - list all current topics\n'

        print 'Usage:'
        print '/list_topics'
    elif command == 'list_receivers':
        print '/list_receivers - list all connected receivers\n'

        print 'Usage:'
        print '/list_receivers'
    elif command == 'list_processes':
        print '/list_processes - list all active processes\n'

        print 'Usage:'
        print '/list_processes'
    else:
        print 'Valid commands:\n'

        print '/help - display this information'
        print '/connect - connect to another user'
        print '/disconnect - disconnect from a connected user'
        print '/add_topic - add topic'
        print '/remove_topic - remove topic'
        print '/list_topics - list all current topics'
        print '/list_receivers - list all connected receivers'
        print '/list_processes - list all active processes\n'

        print 'For more information about a specific command, use /help <command>'


if __name__ == '__main__':
    start_chat(sys.argv)
