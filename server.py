#!/usr/bin/python3
import socket, sys, threading, time, re

class Server():
    """
    The Server receives connections from peers.
    Log connections, log peers, broadcast peers status.
    Receive some message types from peers and reply accordingly
    """

    def __init__(self, port, host='0.0.0.0'):

        self.port = port
        self.host = host
        # Create the socket named "server" to manage incoming connections
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.exc = None

        try:
            # Reuse port immediately if server crashes
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind IP and Port to socket
            self.server.bind((self.host, self.port))

        except socket.error:
            print('Bind failed {}'.format(socket.error))
            sys.exit()

        # Listen for up to 5 simultaneous incoming connections:
        # These connections can be accepted at once and keep accepting more
        # Arbitrary number can be smaller or bigger
        # It does not limit number of connections that will be accepted
        self.server.listen(10)


    def run_server(self):
        """
        Start the server.
        Run infinite loop to accept new connections.
        Create a threat for each connection
        """
        print('Waiting for connections on port {}'.format(self.port))

        # We run a loop and create a new thread for each connection
        while True:
            # Obtain connection information from the connection accepted
            conn, addr = self.server.accept()
            if conn:
                # Creates a thread with the new connection
                threading.Thread(target=self.run_thread, args=(conn, addr)).start()


    def run_thread(self, conn, addr):
        """
        Each thread is processed independently by a constant loop that receives connection data
        :param conn: connection information
        :param addr: part of the peer connection information
        :return: No return, but process of received data
        """
        print('Client connected with ' + addr[0] + ':' + str(addr[1]))

        # TASK 1: Logging Connection
        self.log_connections(conn, addr)
        while True:
            try:
                data = conn.recv(1024)

                if data:
                    reply = str(data.decode('utf-8'))

                    # TASK 2: Logging peers
                    if 'NAME:' in reply:
                        self.log_peer(addr, reply)

                    # TASK 3: Broadcast peers
                    elif '?peers' in reply:
                        self.broadcast_peers()

                    # TASK 4: Broadcast messages
                    elif '@all' in reply:
                        self.broadcast(data, addr)

                    # Print connections
                    elif '?con' in reply:
                        self.get_connections()

                    else:
                        try:
                            pass
                            # self.broadcast(data, addr)

                        except OSError as err:
                            print("OS error: {0}".format(err))
                            self.exit()
                            # self.join()

                else:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()

            except OSError:
                self.clean_conn_peer()
                # self.exit()
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                # self.exit()
                # self.stop()

        # Close connection
        conn.close()



    ### CONNECTIONS
    def log_connections(self, conn, addr):
        """log connection and ip and port"""
        global connections
        connections.add((conn, addr))
        print("Connections: {}".format(connections))

    def get_connections(self):
        """Print logged connections and ip / port"""
        global connections
        print("Get Connections: {}".format(connections))

    ### PEERS
    def log_peer(self, addr, msg):
        """Update table with nicknames, ip and port"""
        global connections
        global peers_online
        global peer_id

        name, port_listen = re.split('::', msg)
        msg_code_name, name = re.split(':', name)
        msg_code_port_listen, port_listen = re.split(':', port_listen)

        new_peer_info = '{}@{}:{}/{}'.format(name, addr[0], port_listen, addr[1] )

        new_peer = ''

        if True:
            if not peers_online:
                new_peer = 'P{}={}@{}:{}/{}'.format(str(peer_id), name, addr[0], port_listen, addr[1])
                print("New Peer {}".format(new_peer))
                peers_online.append(new_peer)

                for i in connections:
                    if '[closed]' not in str(i):
                        if str(addr) == str(i[1]):
                            msg_u_are_online = '[SERVER]: You are online as: ' + new_peer
                            conn = i[0]
                            conn.send(self.encode_msg(msg_u_are_online))


            elif str(new_peer_info) not in str(peers_online):
                peer_id += 1
                new_peer = 'P{}={}@{}:{}/{}'.format(str(peer_id), name, addr[0], port_listen, addr[1])
                print("New Peer {}".format(new_peer))
                # print('{} ______ {}'. format(str(new_peer_info), str(peers_online)))
                peers_online.append(new_peer)

                # print('eeeee {}\n'.format(new_peer))


                for i in connections:
                    if '[closed]' not in str(i):
                        if str(addr) == str(i[1]):
                            msg_u_are_online = '[SERVER]: You are online as: ' + new_peer
                            conn = i[0]
                            conn.send(self.encode_msg(msg_u_are_online))

        time.sleep(0.5)

        # TASK 3: Broadcast peers
        self.broadcast_peers()

    def broadcast_peers(self):
        """Send connected peers
        - if data contains ?peers, print list of connected devices \
            ONLY to the peer who requested
        TODO: - need to put a timer 2 minutes to print on peers
        """
        global peers_online

        msg_peers_online = '[SERVER]: PEERS_ONLINE::'
        for i in peers_online:
            peer_online, port_incoming = re.split('/', i)
            msg_peers_online += str(peer_online) + ', '
        msg_peers_online = msg_peers_online[:-2]

        print(str(msg_peers_online))
        for ii in connections:
            if '[closed]' not in str(ii):
                # Compare ip and port against current connections
                # if str(addr) == str(ii[1]):
                conn = ii[0]

                msg = self.encode_msg(msg_peers_online)
                time.sleep(0.3)

                conn.send(msg)


    def broadcast(self, data, addr):
        """Send message to all if @all in the message
        - TODO create a way to send private message:
        --  if use @port or @user, send message to particular user
        """
        global connections
        data = str(data.decode('utf-8'))
        print(data)

        for i in connections:
            if '[closed]' not in str(i):
                ### Avoid to send msg to itself
                if str(addr) != str(i[1]):
                    conn = i[0]
                    conn.send(self.encode_msg(data))

    ### MAINTENANCE
    def close_incoming(self, conn):
        """
        Identify the dropped connection and close it
        :param conn: Connection details
        :return: No return, but close the connection
        """
        time.sleep(2)
        print('Closing peer {}'.format(conn))
        conn.shutdown(1)
        conn.close()

    def clean_conn_peer(self):
        """
        Remove the connection from connections list
        Identify the linked peer and remove it
        :return: No return, but updates and notifies peers
        """
        # Remove closed connection
        for connection in connections:
            if '[closed]' in str(connection):
                # connections.remove(connection)

                # Remove peer
                remove_peer_ip = '@{}'.format(connection[1][0])
                remove_peer_port = '/{}'.format(connection[1][1])
                for peer in peers_online:
                    if str(remove_peer_ip) and str(remove_peer_port) in str(peer):
                        peers_online.remove(peer)
                        print('Peer disconnected: {}'.format(peer))
                time.sleep(0.8)

                # TASK 3: Broadcast peers
                # Send updated peers list to all peers
                self.broadcast_peers()


    ### SERVER SUPPORT FUNCTIONS
    def stop(self):
        self._is_running = False

    # Ensure sockets are closed on disconnect
    def exit(self):
        print('Closing... {}'.format(self.server))
        self.server.close()

    ### MESSAGES
    def encode_msg(self, msg):
        """Encode messages"""
        msg = bytes(msg, encoding="utf-8")
        return msg


if __name__ == '__main__':
    global connections
    global peers_online
    global peer_id

    peers_online = []
    connections = set()
    peer_id = 0

    # Ask for port number
    PORT = input('Listening port [Default 9876]: ')

    # Set port 9876 if user does not enter the port
    if not PORT:
        PORT = 9876

    server = Server(PORT)
    server.run_server()

