__author__ = 'mats'


import zmq
import sys
from multiprocessing import Process


def start_chat(argv):
    port = argv[1]
    send(port)


def send(port):
    port = str(port)
    context = zmq.Context()
    socket = context.socket(zmq.PUB)

    socket.bind("tcp://*:%s" % port)

    receive_processes = {}

    while True:
        send_msg = raw_input()

        if send_msg[0] == '/':
            args = send_msg.split(' ')

            if args[0] == '/connect':
                receive_port = args[1]
                connect(receive_processes, receive_port)
            elif args[0] == '/disconnect':
                disconnect_port = args[1]
                disconnect(receive_processes, disconnect_port)
            elif args[0] == '/help':
                pass
        else:
            socket.send('%s %s' % (port, send_msg))


def connect(processes, port):
    if port not in processes:
        process = Process(target=receive, args=(port,))
        process.daemon = True
        process.start()
        processes[port] = process
    else:
        print 'already connected'


def disconnect(processes, port):
    if port in processes:
        processes[port].terminate()
        del processes[port]
        print 'disconnected'
    else:
        print 'not connected'


def receive(port):
    port = str(port)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.connect("tcp://localhost:%s" % port)
    socket.setsockopt(zmq.SUBSCRIBE, port)

    while True:
        msg = socket.recv()
        print 'Incoming: ' + msg


if __name__ == '__main__':
    start_chat(sys.argv)