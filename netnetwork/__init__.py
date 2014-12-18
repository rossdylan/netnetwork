import zmq
import os.path
from tornado.web import Application, StaticFileHandler
from tornado.websocket import WebSocketHandler
from zmq.eventloop import ioloop as ZIOLoop
from tornado.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream


ZIOLoop.install()
context = zmq.Context()

Graph = None

class WSHandler(WebSocketHandler):
    def open(self):
        global Graph  # globals :(
        sub_sock = context.socket(zmq.SUB)
        sub_sock.connect("ipc:///tmp/netnetwork.sock")
        sub_sock.setsockopt(zmq.SUBSCRIBE, 'gupdates')
        self.sub_stream = ZMQStream(sub_sock)
        self.sub_stream.on_recv(self.on_zmq_recv)
        print('Opened a new websocket')
        if Graph is not None:
            self.write_message(Graph)

    def on_zmq_recv(self, msg):
        global Graph
        print("Forwarding message to client")
        self.write_message(msg[1])
        Graph = msg[1]

    def on_close(self):
        print("Closing ws stream")
        self.sub_stream.close()


def server():
    """
    Function that spins up the tornado webserver.
    We have two routes, /static which goes to our js and html
    and /ws which is the websocket which just streams stuff from
    a zmq socket.
    """
    static_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
    app = Application([
        (r'/ws', WSHandler),
        (r'/(.*)', StaticFileHandler, {"path": static_path}),
    ])
    app.listen(8080)
    IOLoop.instance().start()
