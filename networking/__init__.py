import sys

# Set to True when the servers are run on a single machine, in threads.
# Set to False if the servers are running on actual machines
LOCAL               = True
PORT                = 50000 # For server-server communication
CLIENT_PORT         = 50001 # For client-server communication
MAX_MSG_SIZE        = 4096
SOCKET_BACKLOG_SIZE = 1024
TIMEOUT             = 1.0   # In seconds
HEADSERVER_IP       = '127.0.0.250'
#DEBUG_PRINT        = False
DEBUG_PRINT         = True
CONFIRM             = 'Thanks'

# When multiple threads are printing at the same time, the newlines are not printed at the same moment as the string
# This function takes care of this. Alternatively, just call sys.stdout.write(<...>)
def safe_print(s):
    sys.stdout.write(s + '\n')
    sys.stdout.flush()

from server.non_blocking_functions import await_confirm, await_reply, connect_to_dst
from Message import Message
from server.MessageReceiver import MessageReceiver
from server.MessageSender import MessageSender
from server.ServerListener import ServerListener
from server.HeadServerListener import HeadServerListener
from server.ServerBroadcaster import ServerBroadcaster
from server.Server import Server
from server.GameServer import GameServer
from server.HeadServer import HeadServer
from client.ClientListener import ClientListener
from client.Client import Client