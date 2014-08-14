try:
    from subprocess import check_output
except:
    import subprocess
    def check_output(l):
        return subprocess.Popen(l,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()[0]
import shlex


class Connection(object):
    """
    Represent a single line returned from the ss command
    """
    def __init__(self, netid, state, recv_q, send_q, local, peer):
        self.netid = netid
        self.state = state,
        self.recv_q = recv_q
        self.send_q = send_q
        self.local = local
        self.peer = peer

    @classmethod
    def from_line(cls, line):
        raw_split = [w for w in line.split(' ') if w != '']
        formatted_split = raw_split[:-2]
        formatted_split.extend([tuple(raw_split[-2].split(':')),
                                tuple(raw_split[-1].split(':'))])
        return Connection(*formatted_split)

    def __repr__(self):
        return 'netid={0}, state={1}, recv_q={2}, send_q={3}, local={4}, peer={5}'.format(
            self.netid, self.state, self.recv_q, self.send_q, self.local, self.peer)

    def __eq__(self, other):
        return other.local[0] == self.local[0] and other.peer[0] == self.peer[0]


def GetConnections():
    """
    Use ss -r --tcp --udp -n to populate a list of Connection objects
    """
    raw_data = check_output(shlex.split('ss -r --tcp --udp -n'))
    return [Connection.from_line(l) for l in raw_data.split('\n')[1:] if l != '']
