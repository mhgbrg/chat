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

            if args[0] == '/connect':
                receive_address = args[1]
                connect(receive_processes, receive_address)
            elif args[0] == '/disconnect':
                disconnect_address = args[1]
                disconnect(receive_processes, disconnect_address)
            elif args[0] == '/help':
                pass
        else:
            socket.send('%s %s' % (address, send_msg))


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