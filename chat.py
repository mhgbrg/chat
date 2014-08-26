__author__ = 'mats'


import zmq
import sys
from socket import gethostbyname, gethostname
from multiprocessing import Process


def start_chat(argv):
    port = argv[1]
    send(port)


def send(port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)

    ip = gethostbyname(gethostname())
    address = ip + ':' + port

    socket.bind("tcp://*:%s" % port)

    receive_processes = {}

    while True:
        send_msg = raw_input()

        if send_msg[0] == '/':
            args = send_msg.split(' ')

            if args[0] == '/exit':
                break
            elif len(args) == 1:
                display_help(args[0][1:])
            else:
                arg1 = args[1]
                if args[0] == '/connect':
                    connect(receive_processes, arg1)
                elif args[0] == '/disconnect':
                    disconnect(receive_processes, arg1)
                elif args[0] == '/help':
                    display_help(arg1)
        else:
            socket.send('%s %s' % (address, send_msg))


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
    else:
        print 'Valid commands:\n'

        print '/help - display this information'
        print '/connect - connect to another user'
        print '/disconnect - disconnect from a connected user\n'

        print 'For more information about a specific command, use /help <command>'


def connect(processes, address):
    if address not in processes:
        process = Process(target=receive, args=(address,))
        process.daemon = True
        process.start()
        processes[address] = process
    else:
        print 'already connected'


def disconnect(processes, address):
    if address in processes:
        processes[address].terminate()
        del processes[address]
        print 'disconnected'
    else:
        print 'not connected'


def receive(address):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.connect("tcp://%s" % address)
    socket.setsockopt(zmq.SUBSCRIBE, address)

    while True:
        msg = socket.recv()
        print msg


if __name__ == '__main__':
    start_chat(sys.argv)