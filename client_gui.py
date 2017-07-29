from PyQt4 import QtCore, QtGui
from GUI import Ui_Chat

import socket
import sys
import threading
import time
import re
import queue
from random import randint, sample


class Incoming():
    """docstring for Peer server role. Listening Incoming connections"""

    def __init__(self, my_name, host_listen="0.0.0.0", port_listen=4000):
        global peers_available
        global incoming_conn
        global incoming_is_started
        global outbound_conn
        global inbound_peers
        global msg_list

        host_listen = "0.0.0.0"
        self.peer_id = ''
        self.name = my_name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('LISTEN AT: {}:{}'.format(host_listen, port_listen))
        self.sock.bind((str(host_listen), int(port_listen)))

        # Listen up to 5 simultaneous connections. It does not limit accepting
        self.sock.listen(5)

        # Create a thread for each accepted connection
        accept = threading.Thread(target=self.accept_con)
        accept.daemon = True
        accept.start()

        # Create a thread for processing each connection
        procces = threading.Thread(target=self.procces_con)
        procces.daemon = True
        procces.start()

    # TASK 1: accept connections
    def accept_con(self):
        """
        Accept connections from peers and add in incomming_connection list
        :return:
        """
        print("[Peer]: accepting connections...")
        while True:
            conn, addr = self.sock.accept()
            conn.setblocking(False)
            if conn:
                incoming_conn.append(conn)

    # TASK 2: process the connections
    def procces_con(self):
        """
        Process each connection in incomming connections list
        :return:
        """
        print("[Peer]: processing connections...")
        while True:
            # Check if there are connections
            if len(incoming_conn) > 0:
                # Read each connection
                for connection in incoming_conn:

                    ### Avoid trying to read from an outbound connection
                    ### TODO: move server connection to outbound list
                    if 'SOCK_STREAM' not in str(connection):
                        try:
                            # Receive data from connection
                            data = connection.recv(1024)
                            if data:
                                # Decode from bytestream to utf-8
                                data = str(data.decode('utf-8'))

                                # Log information from connected peers
                                if 'NAME:' in data:
                                    self.log_peer(data, connection)

                                # Process data that contain MSG_CODe 'CHAT'
                                elif ';CHAT#' in data:
                                    self.log_in_msg(data)

                        # TODO: Catch properly this error
                        except:
                            # self.sock.shutdown(socket.SHUT_RDWR)
                            # self.sock.close()
                            pass
                    else:
                        # Wait millisecond. Do not use overkill loop
                        time.sleep(0.001)

    # TASK 3: Log peer
    def log_peer(self, msg, conn):
        """Update table with nicknames, ip and port"""
        global inbound_peers
        # print('[Peer]: Logging inbound peer {}-{}'.format(msg, conn))

        peer_conn = conn
        # Parse nickname
        nickname_raw, peer_listen_port_raw = re.split('::', msg)
        time.sleep(0.1)

        # Get nickname
        _, nickname = re.split(':', nickname_raw)
        time.sleep(0.1)

        # Get remote connected port from peer
        conn = str(conn)
        peer_conn_port = conn[-7:-2]

        # Get peer listening port
        _, peer_listen_port = re.split(':', peer_listen_port_raw)

        # TODO: get the correct host IP instead of hardcoded localhost
        host = 'localhost'
        time.sleep(0.1)

        # Format peer
        new_peer = '{}@{}:{}/{}'.format(nickname, host, peer_listen_port, peer_conn_port)

        # Log the incoming peer
        if new_peer not in inbound_peers:
            print("New Inbound Peer {}".format(new_peer))
            inbound_peers.append(new_peer)

        # TODO: complete direct connections from peer not registered on the server.
        # check_peer = '{}@{}:{}'.format(nickname, host, peer_listen_port)
        # for peer in peers_available:
        #     if str(check_peer) not in str(peer):
        #         random_peer_id = randint(100000, 999999)
        #         peer_to_peer = 'P{}={}@{}:{}/{}'.format(random_peer_id, nickname, host, peer_listen_port, peer_conn_port)
        #         text_online = '[SERVER]: You are online as: ' + peer_to_peer
        #         msg_u_are_online = bytes(text_online, encoding='utf-8')
        #         peer_conn.sendall(msg_u_are_online)


    # TASK 4: Log
    def log_in_msg(self, msg):
        """
        Log incoming message
        :param msg: contains the data received
        :return:
        """
        global msg_list
        global peers_available

        # Get own peer id
        # TODO: refator to its own method
        if not self.peer_id:
            for name in peers_available:
                if self.name in str(name):
                    self.peer_id, name_raw = re.split('=', str(name))


        # PARSING MESSAGE to extract info for message signature
        # Get the message text
        header, msg_txt = re.split(':', msg)

        if not msg_txt:
            return

        # Get message type and number
        _, MSG_CODE_NUMBER = re.split(';', header)

        # Get the peer id
        sender_peer_id, _ = re.split('R', msg)

        # Get the route list
        route_raw, _ = re.split(';', msg)
        _, route = re.split('R', route_raw)

        # Re-assemble msg signature
        signature = '{};{}'.format(sender_peer_id, MSG_CODE_NUMBER)

        talking_peer = ''
        for name in peers_available:
            if sender_peer_id in str(name):
                _, name_raw = re.split('=', str(name))
                talking_peer, _ = re.split('@', name_raw)

        # Log msg signature if it has not been logged yet
        if signature not in msg_list:
            msg_list.append(signature)

            # Pass the message to all existing connections
            self.msg_to_all(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)

            # PRINT OUTPUT TO USER
            if talking_peer != self.name:
                Chat.ui.list_chat.addItem('{}: {}'.format(talking_peer, msg_txt))
                print('{}: {}'.format(talking_peer, msg_txt))
            else:
                Chat.ui.list_chat.addItem('{}: {}'.format(talking_peer, msg_txt))
                print('{}: {}'.format(self.name, msg_txt))

        # If signature is registered, avoid to resend the message
        elif signature in msg_list:
            pass
            # print("Signature was already registered {}".format(signature))

    # TASK 5: Send message
    def msg_to_all(self, sender_peer_id, route, MSG_CODE_NUMBER, msg_txt):
        """
        Pass message to peers network
        """
        global incoming_conn    # holds the connections
        global outbound_conn    # holds the connections
        global peers_available  # peers list sent by server
        global inbound_peers    # peers from incoming connections

        # Check each incoming connection
        for connection in incoming_conn:

            # Get the remote port of incoming peer. Example port 54321
            sender = str(connection)
            port_outbound = sender[-7:-2]

            # Check each incoming peer
            for peer_available in inbound_peers:

                # Get the remote port of connected peer. Example port 54321
                _, port_remote = re.split('/', peer_available)

                # Compare ports to obtain the correct peer id
                if port_remote == str(port_outbound):
                    # print('port_remote == port_outbound {} == {}'.format(port_remote, port_outbound))

                    # Get peer id
                    peer_id_check, _ = re.split('=', peer_available)

                    # Check that peer id is not in the rout list
                    if str(peer_id_check) not in str(route):
                        # print('peer_id_check not in route {} != {}'.format(peer_id_check, route))

                        # Piggyback my peer id on the route. Add the peer id only once
                        if str(self.peer_id) not in route:
                            route += self.peer_id

                        # Re-assamble signature
                        msg = '{}R{};{}:{}'.format(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)
                        # signature = '{};{}'.format(sender_peer_id, MSG_CODE_NUMBER)
                        # print('>>>MSG IN {}'.format(msg))

                        # Send message to this connection
                        try:
                            msg = bytes(msg, encoding='utf-8')
                            connection.send(msg)
                        except:
                            incoming_conn.remove(connection)
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()

                    # If peer id was already in the route list, avoid to send the message
                    else:
                        pass
                        # print('VOID passing to incoming conn: {} is in {}'.format(peer_id_check, route))

        # Check each outbound connection
        for connection_out in outbound_conn:

            # Get the peer remote listening port
            sender = str(connection_out)
            port_outbound = sender[-6:-2]

            # Check each peer available
            for peer_available in peers_available:

                # Get listening port
                _, port_to = re.split(':', peer_available)

                # Compare the ports to obtain the peer id
                if port_outbound == str(port_to):
                    # print('port_outbound == port_to {} == {}'.format(port_outbound, port_to))

                    # Get the peer id
                    peer_id_check, _ = re.split('=', peer_available)

                    # Check if peer id is not in route list
                    if str(peer_id_check) not in str(route):
                        # print('peer_id_check not in route {} != {}'.format(peer_id_check, route))

                        # Piggyback my peer id on the route. Add the peer id only once
                        if str(self.peer_id) not in route:
                            route += self.peer_id

                        # Re-assamble signature
                        msg = '{}R{};{}:{}'.format(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)
                        # print('>>>MSG OUT {}'.format(msg))

                        # Send the message to this connection
                        try:
                            msg = bytes(msg, encoding='utf-8')
                            connection_out.send(msg)
                        except:
                            outbound_conn.remove(connection_out)
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()

                    # If peer id was already in the route list, avoid to send the message
                    else:
                        print('VOID passing to outbound conn: {} is in {}'.format(peer_id_check, route))



class Outbound():
    """
    Manage connection to server
    Process input from user
    Create outbound connections to other peers
    """

    def __init__(self, name, host_listen='127.0.0.1', port_listen=0000, host_connect='localhost', port_connect=9876):
        """
        Detail to start the connection
        :param name:
        :param host_listen: host where peer wait for incoming connections
        :param port_listen: port for incoming connections
        :param host_connect: host of the server
        :param port_connect: port of the server
        """
        global incoming_conn
        global incoming_is_started
        global outbound_conn
        global inbound_peers
        global msg_number
        global msg_list
        global lock

        # Hack for troubleshooting
        if not port_connect:
            port_connect = 9876

        self.peer_id = ''
        self.name = name
        self.host_listen = host_listen
        self.port_listen = port_listen
        self.port_connect = port_connect
        self._is_running = True

        lock = threading.Lock()

        # -------------------------------------
        # TASK 1: Connect to server
        # Create connection to server
        # TODO: move to a dedicated network method
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print('Connecting to server {} and {}'.format(host_connect, port_connect))
            self.sock.connect((str(host_connect), int(self.port_connect)))
        except ValueError:
            print("Error during connection: {}".format(ValueError))
            # pass

        # Give time to assure the connection
        time.sleep(3)

        # Log connection to server on connection list
        # TODO: move it to outbound connections list
        incoming_conn.append(self.sock)
        # END TASK 1

        # -------------------------------------
        # TASK 2: Prepare to receive data from outbound conn to server and peers
        # Create sub thread for receiving data from outgoing
        msg_recv = threading.Thread(target=self.msg_recv)
        msg_recv.daemon = True
        msg_recv.start()
        # END TASK 2

        # -------------------------------------
        # TASK 3: Prepare attributes for incoming component
        # Create a random port for listening
        # TODO: move to a dedicated network method
        if not port_listen:
            port_listen = randint(5000, 9999)
            self.port_listen = port_listen

        # Send Name and Port to Server
        # TODO: send the listening port too
        # TODO: refactor the log_peer method in Incoming Class
        self.send_my_peer_info()
        # END TASK 3

        # -------------------------------------
        # TASK 4: Connect to peer network
        # Start the connection to peer network
        self.connect_to_net()
        # END TASK 4


        # SECTION ONLY USED IN COMMAND LINE PEER
        # -------------------------------------
        # TASK 5: Process input from user
        # User can type messaeg or registered commands
        # while True:
        #     # Get input from user
        #     input_msg = input('->')
        #
        #     # SUB-TASK 1
        #     # For troubleshooting: print all my connections
        #     if input_msg == '?conn':    # Need to type exact trigger
        #         self.peer_connections()
        #
        #     # For troubleshooting: print all connected incoming peers
        #     elif input_msg == '?inpeers':    # Need to type exact trigger
        #         for peer in inbound_peers:
        #             print("* {}".format(peer))
        #
        #     # Re-used in another task
        #     # For troubleshooting: print peers list provided by server
        #     elif input_msg == '?net':   # Need to type exact trigger
        #         self.peers_net()
        #
        #     # SUB-TASK 2
        #     # For troubleshooting: print all the logged messages
        #     elif input_msg == '?msg':   # Need to type exact trigger
        #         self.print_msg()
        #
        #     # Re-used in another task
        #     # For troubleshooting: manually start connection to peer network
        #     elif input_msg == 'connect-to-net': # Need to type exact trigger
        #         self.connect_to_net()
        #
        #     # SUB-TASK 3
        #     # Send message to network OR disconnect
        #     elif input_msg != 'disconnect-net': # Need to type exact trigger to disconnect
        #         self.msg_to_net(input_msg)
        #
        #     else:
        #         self.sock.close()
        #         sys.exit()
        # END TASK 5


    # -------------------------------------
    # TASK 2: EXECUTION
    def msg_recv(self):
        """Process messages received from outbound connections and server"""
        while True:
            try:
                data = self.sock.recv(1024)

                if data:
                    data = data.decode('utf-8')

                    # SUB-TASK 1
                    # Parse server message to obtain peer id and host information
                    if '[SERVER]: You are online as' in data:
                        # Parse peer id
                        _, peer_info = re.split('as: ', data)
                        peer_id, _ = re.split('=', peer_info)
                        self.peer_id = peer_id

                        # Get my own host IP and port from server
                        host_ip_raw, listen_port_raw = re.split(':', peer_info)

                        # Get clean host ip
                        _, host_ip = re.split('@', host_ip_raw)
                        self.host_listen = host_ip

                        # Get clean listening port
                        listen_port, _ = re.split('/', listen_port_raw)
                        self.port_listen = listen_port

                        # Print for troubleshooting
                        print('[Peer]: My Peer ID: {} Host: {} Listen at Port: {}'.format(self.peer_id,
                                                                                          host_ip, listen_port))

                        Chat.ui.list_chat.addItem('[Peer]: My Peer ID: {} Host: {} Listen at Port: {}'.format(self.peer_id,
                                                                                          host_ip, listen_port))
                        self.run_incoming()

                    # SUB-TASK 2
                    # Parse peers list sent by server
                    elif 'PEERS_ONLINE::' in data:
                        self.get_peers_online(data)

                    # SUB-TASK 3
                    # Parse chat messages
                    elif ';CHAT#' in data:
                        self.log_in_msg(data)

                    # SUB-TASK 4
                    else:
                        print('From Outbound: {}'.format(data))

                # Error when processing, it crashes the thread. Send shutdown
                else:
                    # print('disconnect?')
                    # pass
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()

            # Error with connection, it crashes the thread. Send shutdown
            except:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()

    # SUB-TASK 1
    def run_incoming(self):
        """
        Instantiate the server that receive other peers connections
        :return:
        """
        global incoming_is_started
        if incoming_is_started == False:
            s = Incoming(self.name, self.host_listen, int(self.port_listen))
            incoming_is_started = True

    # SUB-TASK 2
    def get_peers_online(self, data):
        """
        Parse peer list sent by server
        :param data:
        :return:
        """
        global peers_available
        msg_code_name, peers = re.split('::', data)
        peers_available = re.split(', ', peers)
        self.peers_net()


    # -------------------------------------
    # TASK 3:
    def send_my_peer_info(self):
        """
        Send nickname to server and peers in outbound connections
        TODO: Send the listening host
        :return:
        """
        # print("[Peer]: registering in network...")
        msg_code = 'NAME:'

        if self.peer_id:
            peer_info = msg_code + str(self.peer_id) + '=' + str(self.name)
            peer_info += '::PORT_LISTEN:{}'.format(self.port_listen)

        else:
            peer_info = msg_code + str(self.name)
            peer_info += '::PORT_LISTEN:{}'.format(self.port_listen)

        # !!! TODO update way of sending my peer info
        msg = bytes(str(peer_info), encoding="utf-8")
        for c in incoming_conn:
            if c:
                if '[closed]' not in str(c):
                    try:
                        c.send(msg)
                    except:
                        incoming_conn.remove(c)
                        print('removing {}'.format(str(c)))

        for c in outbound_conn:
            if c:
                if '[closed]' and '9876' not in str(c):
                    try:
                        c.send(msg)
                    except:
                        incoming_conn.remove(c)
                        print('removing {}'.format(str(c)))
        return


    # -------------------------------------
    # TASK 4: EXECUTION
    def connect_to_net(self):
        """
        Automatically connect to register on server and connect to network
        :return:
        """
        print('[Peer]: Connecting to network')

        # SUB-TASK 1: Print formatted list of peers obtained with TASK 2, SUB-TASK 2
        # Enable for troubleshooting only
        time.sleep(2)
        self.peers_net()

        # SUB-TASK 2: Connect to peer network
        time.sleep(1)
        self.start_outbound_conn()

        # SUB-TASK 3: Print peer connections.
        # Enable for troubleshooting only. Disabled for hiding verbose output
        # time.sleep(1)
        # self.peer_connections()

    # SUB-TASK 1
    def peers_net(self):
        """
        Print formatted list of peers registered in server
        :return:
        """
        print('[Peer]: local list of peers:')

        # Add user in list
        Chat.ui.list_users.clear()
        for i in peers_available:
            nickname_raw, _ = re.split('@', i)
            _, nickname = re.split('=', nickname_raw)
            Chat.ui.list_users.addItem(nickname)
            print('*** {}'.format(i))

    # SUB-TASK 2
    # STEP 1: Select peers to create connection
    def start_outbound_conn(self):
        q_peers = []
        peer_ip_ports = []

        # Create a queue to feed the threads
        q = queue.Queue()

        # If there is any peers from server
        if peers_available:
            # Check the peers connected list passed by server
            for peer_available in peers_available:
                name, host = re.split('@', peer_available)  # Get name and host
                remote_ip, remote_port = re.split(':', host)  # Get ip and port from host

                # If port is Not Own listen port
                if int(remote_port) != int(self.port_listen):
                    peer_ip_ports.append((remote_ip, int(remote_port)))

        else:
            print('No peers available')
            return

        # If there is any outbound connection
        if outbound_conn:
            for ip_port in peer_ip_ports:
                # Check if the port is in an outbound connection
                # for connection in outbound_conn list:
                if str(ip_port[1]) not in str(outbound_conn):
                    # Add peer ip and port to the list
                    q_peers.append(ip_port)
                    q_peers = self.check_incomming_peer(ip_port, q_peers)

        # If outbound_conn list was empty
        else:
            for ip_port in peer_ip_ports:
                # Add peer ip and port to the list
                q_peers.append(ip_port)
                q_peers = self.check_incomming_peer(ip_port, q_peers)

        # If there were no peers for outbound connections
        if not q_peers:
            print('[Peer]: No peers qualified for outbound connections')
            return

        # If there is at least 1 peer for outbound connections
        else:
            # Select randomly 2 peers or at least 1.
            q_selected = []
            a = sample(range(0, len(q_peers)), 1)

            if len(q_peers) > 1:
                a = sample(range(0, len(q_peers)), 2)

            # Append tupple ip_port to queue
            for index, item in enumerate(q_peers):
                for i in a:
                    if index == i:
                        q_selected.append(item)

        # Pass to queue
        for item in q_selected:
            q.put_nowait(item)

        # Pass to outgoing connection thread:
        ## Pass to the wrapper and from wrapper to outgoing connection
        for _ in q_peers:
            threading.Thread(target=self.wrapper_connection,
                             args=(self.connect_outbound, q)).start()

        q.join()

    # STEP 1 Cleaning: Removing peers if already in incoming connection
    def check_incomming_peer(self, port, list):
        """
        Remove peer from list if is already in an incoming connection
        :param port: peer listening port
        :param list: local inbound peers list
        :return:
        """
        for i in inbound_peers:
            if str(port) in str(i):
                list.remove(port)
                # print('Removing Port {}'.format(port))
        return list

    # STEP 2: Wrap the function passing data from queue
    def wrapper_connection(self, b, q):
        """
        Take 1 item from queue stack to extract ip and port
        """
        while True:
            try:
                ip_port = q.get(timeout=3)
                host_connect = ip_port[0]
                work = ip_port[1]
            except queue.Empty:
                return

            # Lock shared resource to create connection and register in outbound connection list
            lock.acquire()
            self.connect_outbound(host_connect, work)
            lock.release()

            time.sleep(0.5)
            # Send my peer info to remote peer
            self.send_my_peer_info()

            # Remove object from stack to get the next one
            q.task_done()

    # STEP 3: Create outbound connection to remote peer
    def connect_outbound(self, host_connect, port_connect):
        """
        Create socket and connect to remote peer
        :param host_connect: host where peer is located
        :param port_connect: port where peer is listening
        :return:
        """
        # Create outbound socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to remote peer
            self.sock.connect((str(host_connect), int(port_connect)))
            time.sleep(0.2)

            # Add Outbound connection to connections list
            outbound_conn.append(self.sock)

        # If connection fails
        except:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()


    # -------------------------------------
    # TASK 5: EXECUTION

    # SUB-TASK 1
    def peer_connections(self):
        """
        Print current connections list
        :return:
        """
        print('--- Connections ---')
        for c in incoming_conn:
            if 'SOCK_STREAM' and '9876' in str(c) and '[closed]' not in str(c):
                print('OUT server: {}'.format(c))
        for c in outbound_conn:
            print('OUT peer: {}'.format(c))
        for c in incoming_conn:
            if 'type=2049' in str(c) and '[closed]' not in str(c):
                print('IN peer: {}'.format(c))
        for c in incoming_conn:
            if '[closed]' in str(c):
                print('Closed: {}'.format(c))

    # SUB-TASK 2
    def print_msg(self):
        """
        Print list of messages
        :return:
        """
        global msg_list
        for i in msg_list:
            print('MSG: {}'.format(i))

    # SUB-TASK 3
    # STEP 1, Creating a message
    def msg_to_net(self, msg):
        """
        Assemble the formatted message
        :param msg: input enter by user
        :return: pass to send it
        """
        global msg_number
        MSG_CODE = 'CHAT'

        # R = route
        route = self.peer_id
        msg = '{}R{};{}#{}:{}'.format(self.peer_id, route, MSG_CODE, msg_number, msg)
        # print('MSG formatted: {}'.format(msg))
        msg_number += 1

        # Pass msg to log its signature
        self.log_in_msg(msg)

    # SUB-TASK 3
    # STEP 2, Logging the message
    def log_in_msg(self, msg):
        global msg_list
        global peers_available


        # Get own peer id
        if not self.peer_id:
            for name in peers_available:
                if self.name in str(name):
                    self.peer_id, name_raw = re.split('=', str(name))

        # Get the message text
        header, msg_txt = re.split(':', msg)

        if not msg_txt:
            return

        # Get message type and number
        _, MSG_CODE_NUMBER = re.split(';', header)

        # Get the peer id
        sender_peer_id, _ = re.split('R', msg)

        # Get the route list
        route_raw, _ = re.split(';', msg)
        _, route = re.split('R', route_raw)

        # Re-assamble signature
        signature = '{};{}'.format(sender_peer_id, MSG_CODE_NUMBER)

        talking_peer = ''
        for name in peers_available:
            if sender_peer_id in str(name):
                _, name_raw = re.split('=', str(name))
                talking_peer, _ = re.split('@', name_raw)

        # Register signature if is not in the list
        if signature not in msg_list:
            msg_list.append(signature)
            # print('Appending Signature: {}'.format(signature))

            self.msg_to_all(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)

            if talking_peer != self.name:
                Chat.ui.list_chat.addItem('{}: {}'.format(talking_peer, msg_txt))
                print('{}: {}'.format(talking_peer, msg_txt))
            else:
                Chat.ui.list_chat.addItem('{}: {}'.format(talking_peer, msg_txt))
                print('{}: {}'.format(self.name, msg_txt))

        # If signature is registered, avoid to resend the message
        elif signature in msg_list:
            pass
            # print("Signature was already registered {}".format(signature))


    # SUB-TASK 3
    # STEP 3, Sending the message
    def msg_to_all(self, sender_peer_id, route, MSG_CODE_NUMBER, msg_txt):
        """
        Pass message to peer clients
        peers: global holds the connections
        """
        global incoming_conn
        global outbound_conn
        global peers_available
        global inbound_peers

        # Check each incomming connection
        for connection in incoming_conn:

            # Get the remote port of incoming peer. Example port 54321
            sender = str(connection)
            port_outbound = sender[-7:-2]

            # Check each incomming peer
            for peer_available in inbound_peers:

                # Get the remote port of connected peer. Example port 54321
                _, port_remote = re.split('/', peer_available)

                # Compare ports to obtain the correct peer id
                if port_remote == str(port_outbound):
                    # print('port_remote == port_outbound {} == {}'.format(port_remote, port_outbound))

                    # Get peer id
                    peer_id_check, _ = re.split('=', peer_available)

                    # Check that peer id is not in the rout list
                    if str(peer_id_check) not in str(route):
                        # print('peer_id_check not in route {} != {}'.format(peer_id_check, route))

                        # Piggyback my peer id on the route. Add the peer id only once
                        if str(self.peer_id) not in route:
                            route += self.peer_id

                        # Re-assamble signature
                        msg = '{}R{};{}:{}'.format(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)
                        # signature = '{};{}'.format(sender_peer_id, MSG_CODE_NUMBER)
                        # print('>>>MSG IN {}'.format(msg))

                        # Send message to this connection
                        try:
                            msg = bytes(msg, encoding='utf-8')
                            connection.send(msg)
                        except:
                            incoming_conn.remove(connection)
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()

                    # If peer id was already in the route list, avoid to send the message
                    else:
                        pass
                        # print('VOID passing to incoming conn: {} is in {}'.format(peer_id_check, route))

        # Check each outbound connection
        for connection_out in outbound_conn:

            # Get the peer remote listening port
            sender = str(connection_out)
            port_outbound = sender[-6:-2]

            # Check each peer available
            for peer_available in peers_available:

                # Get listening port
                _, port_to = re.split(':', peer_available)

                # Compare the ports to obtain the peer id
                if port_outbound == str(port_to):
                    # print('port_outbound == port_to {} == {}'.format(port_outbound, port_to))

                    # Get the peer id
                    peer_id_check, _ = re.split('=', peer_available)

                    # Check if peer id is not in route list
                    if str(peer_id_check) not in str(route):
                        # print('peer_id_check not in route {} != {}'.format(peer_id_check, route))

                        # Piggyback my peer id on the route. Add the peer id only once
                        if str(self.peer_id) not in route:
                            route += self.peer_id

                        # Re-assamble signature
                        msg = '{}R{};{}:{}'.format(sender_peer_id, route, MSG_CODE_NUMBER, msg_txt)

                        # Send the message to this connection
                        try:
                            msg = bytes(msg, encoding='utf-8')
                            connection_out.send(msg)
                        except:
                            outbound_conn.remove(connection_out)
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()

                    # If peer id was already in the route list, avoid to send the message
                    else:
                        pass
                        # print('VOID passing to outbound conn: {} is in {}'.format(peer_id_check, route))

    def close_app(self):
        self.sock.close()
        sys.exit()

class MainDialog(QtGui.QMainWindow):

    def __init__(self):
        super(MainDialog, self).__init__()

        global incoming_conn
        global peers_available
        global incoming_is_started
        global outbound_conn
        global inbound_peers
        global lock
        global msg_number
        global msg_list

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        # self.ui.help_button.connect(self.ui.help_button, QtCore.SIGNAL("clicked()"), self.help)

        ### Button connect
        self.ui.connect_button.connect(self.ui.connect_button, QtCore.SIGNAL("clicked()"), self.connect)
        ### Button send
        self.ui.send_button.connect(self.ui.send_button, QtCore.SIGNAL("clicked()"), self.send2_msg)
        self.ui.msg_text.connect(self.ui.send_button, QtCore.SIGNAL("returnPressed()"), self.send2_msg)

        self.ui.disconnect_button.connect(self.ui.disconnect_button, QtCore.SIGNAL("clicked()"), self.close_app)


    def connect(self):
        global to_server

        msg_connecting = "[PEER]: connecting..."
        self.ui.list_chat.addItem(msg_connecting)

        # Parse the name, ignore if empty
        name_raw = self.ui.line_nickname.text()
        if not name_raw:
            self.ui.list_chat.addItem('[PEER]: please enter a nickname...')
            return

        # Disable buttons after connection
        self.ui.connect_button.setEnabled(False)
        self.ui.line_nickname.setEnabled(False)
        self.ui.line_ip.setEnabled(False)
        self.ui.line_port.setEnabled(False)

        name_raw = name_raw[:20]
        name = name_raw.replace(" ", "_")

        host_connect = self.ui.line_ip.text()
        port_connect = self.ui.line_port.text()

        # Harcoded listening attributes
        # TODO: Allow user to enter correct host and port to listen
        host_listen = '0.0.0.0'
        port_listen = 0

        # Connect to server
        to_server = Outbound(
            name, host_listen=host_listen, port_listen=port_listen, host_connect=host_connect,
            port_connect=port_connect)

        msg_connected = "[PEER]: connected..."
        self.ui.list_chat.addItem(msg_connected)


    def send2_msg(self):
        global to_server
        msg_text = self.ui.msg_text.text()
        Outbound.msg_to_net(to_server, msg_text)
        # Print in backend console
        # print(msg_text)

    def close_app(self):
        global to_server
        Outbound.close_app(to_server)


    # Incompleted to show connection information
    # def connection(self):
    #     a = self.line_ip.text()
    #     b = self.line_port.text()
    #     c = self.line_nickname.text()
    #     connection = '{}@{}:{}'.format(c, a, b)
    #     print('{}@{}:{}'.format(c, a, b))
    #     # self.list_chat.addItem(connection)
    #     self.list_users.addItem(connection)

    # Incompleted to provide help information
    # def help(self, data):
    #     print('Help button')
        # self.ui.list_chat.addItem(data)
        # self.ui.list_users.addItem(data)



def main():
    global incoming_conn
    global peers_available
    global incoming_is_started
    global outbound_conn
    global inbound_peers
    global lock
    global msg_number
    global msg_list

    global Chat
    global to_server

    incoming_conn = []
    peers_available = []
    incoming_is_started = False
    outbound_conn = []
    inbound_peers = []
    msg_number = 0
    msg_list = []

    ### Start GUI
    app = QtGui.QApplication(sys.argv)
    Chat = MainDialog()
    Chat.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
