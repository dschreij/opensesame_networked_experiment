# OpenSesame example: networked experiment
This is an example of how to write a networked experiment using the [OpenSesame experiment builder](https://github.com/smathot/OpenSesame). This example implements a simple chat interface between the server and client experiments.

You find three main files here.

- A server listening for incoming connections: ChatServer.opensesame.tar.gz
- A client connecting to that server: ChatClient.opensesame.tar.gz
- An external script item that does all the heavy lifting in terms of communication: communicator.py. This file is provided separately just as a convenience, but it is already included in the file pools of *both* the client and the server.

First you need to set up ChatServer.opensesame.tar.gz. Look up the IP address of the computer you are running this experiment on and remember it for later use. You may also want to change the port in its included communicator.py file; the default is 5001. Start up the server by running the experiment. It will wait  until it detects a connections from the client.

Next you will have to set-up the *client* by editting and then running ChatClient.opensesame.tar.gz. This can be on a different computer, but may also be on the same computer as the server's. In the latter case, use 127.0.0.1 as the IP address to connect to. In the Configure script item (which occurs first) change the exp.set("remote_ip") entry at the bottom so that the IP-address corresponds what that of the server. If you have changed the port from its default 5001, you will also need to change this in the communicator.py enclosed with the client. Both server and client should be set to communicate on the same port, otherwise they will not find each other. After this, start the client.

You should now see that both the server and the client show a prompt to enter a message. Anything typed and sent on one computer will also appear on the other.

For the documentation of the communictor.py, please refer to the doc folder. I have not yet found out, how to easily export Python docstring to markdown, such that they are easily renderable in Github's README.md.

**Please note:** this experiment was created in OpenSesame 2 and may not work as intended with the newer OpenSesame 3 