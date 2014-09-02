import zmq
import json
from netnetwork.conn import GetConnections
import time


class GraphAggregator(object):
    def __init__(self):
        self.connections = ()
        self.changed = False

    def add_conn(self, local, peer):
        if (local, peer) not in self.connections:
            print("Adding conn: {0} -> {1}".format(local, peer))
            self.connections += ((local, peer),)
            self.changed = True

    def rem_conn(self, local, peer):
        if (local, peer) in self.connections:
            print("Removing conn: {0} -> {1}".format(local, peer))
            self.connections = tuple(frozenset(self.connections) - frozenset(((local, peer),)))
            self.changed = True

    def graph(self):
        data = {'nodes': [], 'links': []}
        nodeIndexes = {}
        index = 0
        for conn in self.connections:
            if conn[0] not in nodeIndexes and conn[0] != 'localhost.localdomain':
                data['nodes'].append({'name': conn[0], 'x': 500, 'y': 300})
                nodeIndexes[conn[0]] = index
                index += 1
            if conn[1] not in nodeIndexes and conn[1] != 'localhost.localdomain':
                data['nodes'].append({'name': conn[1], 'x': 500, 'y': 300})
                nodeIndexes[conn[1]] = index
                index += 1
            if conn[1] != 'localhost.localdomain' and conn[0] != 'localhost.localdomain':
                data['links'].append({
                    'source': nodeIndexes[conn[0]],
                    'target': nodeIndexes[conn[1]]
                })
        self.changed = False
        return data


def aggregator():
    """
    Takes input from multiple computers and aggregates their connection data
    into a single graph that is then pushed out to the graph webserver
    """
    import sys
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.bind(sys.argv[1])
    pub = context.socket(zmq.PUB)
    pub.bind("ipc:///tmp/netnetwork.sock")
    sub.setsockopt(zmq.SUBSCRIBE, "add_conn")
    sub.setsockopt(zmq.SUBSCRIBE, "rem_conn")
    agg = GraphAggregator()
    while True:
        topic, msg = sub.recv_multipart()
        conns = json.loads(msg)
        if topic == 'add_conn':
            agg.add_conn(conns['local'], conns['peer'])
        else:
            agg.rem_conn(conns['local'], conns['peer'])
        if agg.changed:
            print("Sending aggregated data")
            pub.send_multipart(['gupdates', json.dumps(agg.graph())])


def collector():
    import sys
    """
    Run on a host and point at the box hosting the aggregator
    """
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.connect(sys.argv[1])
    prev_conns = []
    while True:
        conns = GetConnections()
        for conn in conns:
            if conn not in prev_conns:
                pub.send_multipart(["add_conn",
                                    json.dumps({
                                        'local': conn.local[0],
                                        'peer': conn.peer[0]
                                    })])

        for pconn in prev_conns:
            if pconn not in conns:
                pub.send_multipart(["rem_conn",
                                    json.dumps({
                                        'local': pconn.local[0],
                                        'peer': pconn.peer[0]
                                    })])
        prev_conns = conns
        time.sleep(15)
