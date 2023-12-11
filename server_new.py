# Author: Caleb Ingram
# Date: 12/7/2023
# Email: ingramca@oregonstate.edu 
#
#   SOURCES:
#       The following were inspired by https://docs.python.org/3/howto/sockets.html:
#           binding a server socket to an IP client_socketess and port using the socket method bind()
#           queue up a number of socket requests using socket method listen()
#           accept client connections to a server using socket method accept()
#
#       The following line was taken directly from assignment instructions to reuse a socket address:
#           s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEclient_socket, 1)
#
#       The following was inspired by https://www.geeksforgeeks.org/clear-screen-python/
#           os.system('clear') to clear the terminal for visual clarity

import socket
import os

def prep_send_to_client(connection, mandatory_input=[]):
    maintain = True

    # get message to send to client
    if mandatory_input == []:
        message_to_client = input("Enter Input > ")
    elif mandatory_input == ["r","p","s"]:
        while message_to_client not in mandatory_input:
            message_to_client = input('Please enter your move (R/P/S): > ')

    # shut down if prompted, otherwise encode and send a nonempty message <4096 bytes
    if message_to_client == '/q':
        maintain = False

    elif message_to_client == '':
        print("Please try again")
        return prep_send_to_client(connection)
    
    elif len(message_to_client) > 4096:
        print(f"Your message was {len(message_to_client)} characters. Please try again \
              with a shorter message (4096 byte max)")
        return prep_send_to_client(connection)
    
    else:
        maintain = True
                    
    return maintain, message_to_client

def receive_from_client(connection):
    maintain_connection = True
    # receive and decode a message from the client through an established connection
    message_from_client = connection.recv(4096)
    message_from_client = message_from_client.decode()

    # display received message, prompt termination if client sent "/q"
    if message_from_client == '/q':
        maintain_connection = False

    return maintain_connection, message_from_client

def shut_down():
    return False, False

def print_chat_instructions():
    print("\nInstructions:")
    print("   -Please wait for prompt to input a message to the client.")
    print("   -Type /q to quit.")
    print('   -Type "rps" to play a round of rock-paper-scissors\n')

def print_rps_instructions():
    print("\nInstructions:")
    print("   -Type /q to quit.")
    print('   -Type R to play rock, P for paper, or S for scissors\n')

def calculate_and_print_rps_results(player1_move, player2_move):
    player1_move = player1_move.lower()
    player2_move = player2_move.lower()

    player1 = "Server"
    player2 = "Client"
    winner = None

    if player1_move == player2_move:
        pass
    elif player1_move == "r" and player2_move == "p":
        winner = player2
    elif player1_move == "r" and player2_move == "s":
        winner = player1
    elif player1_move == "p" and player2_move == "r":
        winner = player1
    elif player1_move == "p" and player2_move == "s":
        winner = player2
    elif player1_move == "s" and player2_move == "p":
        winner = player1
    elif player1_move == "s" and player2_move == "r":
        winner = player2

    if player1_move == "r":
        player1_move = "ROCK"
    elif player1_move == "p":
        player1_move = "PAPER"
    elif player1_move == "s":
        player1_move = "SCISSORS"
    
    if player2_move == "r":
        player2_move = "ROCK"
    elif player2_move == "p":
        player2_move = "PAPER"
    elif player2_move == "s":
        player2_move = "SCISSORS"

    print("Rock-paper-scissors results:")
    print(f"Server played {player1_move}; Client played {player2_move}")
    if winner:
        print(f"The winner is the {winner}")
    else:
        print("Tie game!")
    
def respond_to_rps_request(conn):
    #print instructions
    print("\nThe client wants to play a round of rock-paper-scissors!")
    print_rps_instructions()

    # send client move
    client_move = ""
    while client_move.lower() not in ["r","p","s","/q"]:
        client_move = input("Please enter your move (R/P/S): > ")
    client_move = client_move.lower()
    conn.sendall(client_move.encode())

    if client_move == "/q":
        print("Rock-paper-scissors denied. Returning to normal chat mode.\n")
        return
    
    # get server move
    print("Getting server's move...")
    server_move = conn.recv(4096)
    server_move = server_move.decode()

    # print results
    calculate_and_print_rps_results(client_move, server_move)

    print("\nReturning to normal chat mode.")
    
def initiate_rps(conn):
    # print instructions
    print("\nYou have opted to play a round of rock-paper-scissors!")
    print_rps_instructions()

    # get client's move
    print("Waiting for client's move...")
    client_move = conn.recv(4096) 
    client_move = client_move.decode()
    if client_move == "/q":
        print("Rock-paper-scissors denied by client. Returning to normal chat mode.\n")
        print("Waiting for client to send a chat...")
        return

    # send server's move
    server_move = ""
    while server_move.lower() not in ["r","p","s","/q"]:
        server_move = input("Please enter your move (R/P/S): > ")
    server_move = server_move.lower()
    conn.sendall(server_move.encode())

    calculate_and_print_rps_results(server_move, client_move)

    print("\nReturning to normal chat mode. Waiting for client chat...")

def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # turn on a socket that can listen for connection requests
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', port))
        s.listen()
        os.system('clear')
        print("Listening...")

        # accept connection requests, track the connection and the client address information
        connection, client_socket = s.accept()

        # use the connection to receive and send messages
        with connection:
            print(f"Server listening on: localhost on port: {port}")
            print(f"Connected by {client_socket}")
            print_chat_instructions()

            still_sending = True
            still_receiving = True
            incoming_message = ""
            outgoing_message = ""

            while still_receiving and still_sending:
                if still_receiving:
                    still_sending, incoming_message = receive_from_client(connection)
                    
                    print(f"Client: {incoming_message}")

                    if incoming_message == '/q':
                        print("Client has requested a disconnection. Goodbye!")
                        still_receiving, still_sending = shut_down()
                        break
                    if incoming_message.lower() == 'rps':
                        respond_to_rps_request(connection)

                if still_sending:
                    still_receiving, outgoing_message = prep_send_to_client(connection)
                    connection.sendall(outgoing_message.encode())

                    if outgoing_message == '/q':
                        print("Shutting down!")
                        still_receiving, still_sending = shut_down()
                        break
                    if outgoing_message == 'rps':
                        initiate_rps(connection)

if __name__ == '__main__':
    PORT = 5599
    start_server(PORT)
