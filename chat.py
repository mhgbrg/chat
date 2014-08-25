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

                receive_processes[receive_port] = Process(target=receive, args=(receive_port,))
                receive_processes[receive_port].daemon = True
                receive_processes[receive_port].start()
            elif args[0] == '/disconnect':
                disconnect_port = args[1]
                receive_processes[disconnect_port].terminate()
            elif args[0] == '/help':
                pass
        else:
            socket.send('%s %s' % (port, send_msg))


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