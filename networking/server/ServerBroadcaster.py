import socket
import threading
import time

from networking import DEBUG_PRINT, LOCAL, MAX_MSG_SIZE, PORT, \
                       safe_print


# This class is used to ping all neighbouring servers, listen for replies and update the server's 
# peer list accordingly.
class ServerBroadcaster(threading.Thread):
    def __init__(self, server, interval):
        threading.Thread.__init__(self)
        self.server = server
        self.interval = interval
        # List of peers that have replied since the previous ping
        # Used to get rid of outdated peers
        self.neighbours = []

    def sb_print(self, s):
        if DEBUG_PRINT:
            safe_print('[SERVERBROADCASTER {:d}]: {:s}'.format(self.server.identifier, s))

    # This functions adds a host to our peer list if it is not already in there,
    # and if it is not equal to our server's hostname
    # It also updates the server's peer list
    def add_neighbour(self, host):
        if host not in self.neighbours and host != self.server.host:
            self.neighbours.append(host)
        with self.server.peer_lock:
            if host not in self.server.neighbours and host != self.server.host:
                self.server.neighbours.append(host)

    # Given a (UDP) socket, checks if there are ping replies to process.
    def check_ping_replies(self, s):
        try:
            # Check if there is a reply
            m, src = s.recvfrom(MAX_MSG_SIZE)
            # There was! Update our neighbours list if necessary
            # The message itself ('m') should be the IP address of the replying server
            #self.sb_print('Reply from {:s}: {:s}'.format(str(src), m))
            self.add_neighbour(m)
        except:
            # Got no message, do nothing
            pass

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.setblocking(0)

        # Start with a ping, then re-ping every <interval> seconds
        timestamp = time.time()
        ping = True
        while True:
            if ping:
                # We're pinging now; update timestamp
                ping = False
                timestamp = time.time()
                # Update the server's neighbour list with the data gathered from our previous ping
                # By replacing the list entirely, we deal with the issue of removing outdated entries
                with self.server.peer_lock:
                    self.server.neighbours = self.neighbours
                self.neighbours = []
                s.sendto('Ping from ServerBroadcaster {:d}'.format(self.server.identifier), ('<broadcast>', PORT))
            else:
                self.check_ping_replies(s)
                # If our Server thread has told us to stop, we stop; otherwise, we yield to another thread
                with self.server.stop_lock:
                    if self.server.stop:
                        # Close socket and stop
                        s.close()
                        self.sb_print('Stopped.')
                        return
                # Yield
                time.sleep(0)
                # Check if we need to send another ping
                if time.time() - timestamp > self.interval:
                    ping = True
     