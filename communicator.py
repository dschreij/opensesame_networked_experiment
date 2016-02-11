"""Establishes a connection between two computers and enables them to send simple string messages to each other.
Instances of this class run as separate processes (threads) in the background and thus continuously listen for incoming messages.
Messages in the messagelist are stored as (message,origin) tuples, where message is the message string and origin is the IP address of the pc that sent the message
(use "local" as origin to indicate sent messages, if you want to store these in messageList as well)."""




import threading
import socket
import select
try:
    import openexp.keyboard
except:
    print "Could not import openexp.keyboard"

class Chatbox(threading.Thread):
	"""Establishes a connection between two computers and enables them to send simple string messages to each other.
	Instances of this class run as separate processes (threads) in the background and thus continuously listen for incoming messages.
	Messages in the messagelist are stored as (message,origin) tuples, where message is the message string and origin is the IP address of the pc that sent the message
	(use "local" as origin to indicate sent messages, if you want to store these in messageList as well).
	"""

	def __init__(self, role, addr="", port=5001, receivedMessageList=[], sentMessageList=[], kbinput=None):
		"""Constructor - called when instance of class is created

		Args:
			role (str): Allowed values: {"server","client"}.
				Indicate whether this computer is a "server" (i.e. listens for incoming connections from other computers)
				or a "client" (i.e. connects to another computer that is listening for connections).

		Kwars:
			addr (str): The address of the computer to connect to (client only, empty when running as "server") (default = "")
			port (int): The port to either listen to (in server mode) or connect to at the remote machine (in client mode) (default = 5001)
			messageList (list): The reference to the list to append the received messages to (default = [] (i.e. a new list)).
			kbinput (openexp.keyboard): Optional reference to an openexp keyboard object that is used to break from 'waiting for connection' loop if Escape is pressed in OpenSesame
		"""

		self.__role = role
		self.__addr = addr
		self.__port = port
		self.__recvMsgList = receivedMessageList
		self.__sentMsgList = sentMessageList
		self.__msgList = []
		threading.Thread.__init__ ( self )

		if role=="server":
			self.__listen(addr,port,kbinput)
			self.setName("OSChatServer")
		elif role=="client":
			self.__connect(addr,port)
			self.setName("OSChatClient")
		else:
			raise TypeError("Invalid chatbox type specified: please use client or server only")

		self.__connected = True
		self.__running = True
		self.start()

	def __listen(self,addr,port,kbinput):
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.settimeout(1.0)
		serversocket.bind((addr,port))
		serversocket.listen(1)

		print "Waiting for connections"
		self.waitingForClient = True
		while self.waitingForClient:
			try:
				print "Still waiting...."
				(s, details) = serversocket.accept()
				self.waitingForClient = False
			except socket.timeout:
				if kbinput != None:
					kbinput.get_key()
					continue
		print "Connection established to {0}".format(details)
		self.__socket = s

	def __connect(self, addr, port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((addr, port))
		except socket.gaierror:
			try:
				s.connect((socket.gethostbyname(addr),port))
			except:
				raise Exception("Unable to find or connect to remote computer {0}:{1}".format(addr,port))
		print "connected to {0}:{1}".format(addr,port)
		self.__socket = s

	def get_addr(self):
		"""
		Returns:
			str. the adress of the remote machine (in client mode) or the address of the local machine (in server mode, probably an empty string)
		"""
		return self.__addr

	def get_port(self):
		"""
		Returns:
			int. the port to which was connected at the remote machine (in client mode) or to which local machine listens to (in server mode)
		"""
		return self.__port

	def send_message(self,message):
		"""
		Args:
			message (str): the message to send to the remote machine
		"""

		self.__socket.send(message)
		self.__sentMsgList.append((message,"local"))
		self.__msgList.append((message,"local"))

	def get_messagelist(self):
		"""
		Returns:
			list. The reference to the list in which received messages are stored
		"""
		return self.__msgList

	def get_and_clear_received_messages(self):
		"""
		Same as 'get_received_messages' but also clears the received messages list

		Returns:
			list. A list of received messages (i.e. messages of which the origin != "local")
		"""
		#return filter(lambda (m,s): s!="local", self.__msgList)
		currentList = self.__recvMsgList
		self.__recvMsgList = []
		return self.currentList

	def get_received_messages(self):
		"""
		Returns:
			list. A list of received messages (i.e. messages of which the origin != "local")
		"""
		#return filter(lambda (m,s): s!="local", self.__msgList)
		return self.__recvMsgList

	def get_sent_messages(self):
		"""
		Returns:
			list. A list of sent messages (i.e. messages of which the origin == "local")
		"""
		#return filter(lambda (m,s): s=="local", self.__msgList)
		return self.__sentMsgList

	def run(self):
		"""
		Keep listening for incoming messages and append them to messageList when received.
		Main thread loop that should not be called directly, but through Chatbox.start() (inherited from Thread)
		When the constructor is called, the run method is automatically invoked after a connection is established.
		"""
		print "Listening for messages"
		while self.__running:
			try:
				r, _, _ = select.select([self.__socket], [], [], 0)
				do_read = bool(r)

				if do_read:
					data = self.__socket.recv(1024)
					if data in ["", "/exit"]:
						print "The other side closed the connection"
						self.__running = False
					else:
						remote_ip,port = self.__socket.getsockname()
						self.__recvMsgList.append((data,remote_ip))
						self.__msgList.append((data,remote_ip))
			except socket.error as e:
				print "Socket error: ", e.strerror
				self.__running = False

		print "Closing connection"
		self.__socket.close()

	def stop(self):
		""" Stop listening for incoming messages, close the socket and kill the thread."""
		self.__running = False

#-------------------------------------------------------------------
# Functions required to be usable as external script item in opensesame
#-------------------------------------------------------------------

def prepare(item):
	return True

def run(item):
	exp = item.experiment

	kb = openexp.keyboard.keyboard(exp,timeout=100)
	if exp.get("role") == "client":
		ip = exp.get("remote_ip")
		exp.cb = Chatbox("client", addr=ip, kbinput=kb)
	else:
		exp.cb = Chatbox("server", kbinput=kb)
	return True
