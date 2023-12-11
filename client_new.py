# Author: Caleb Ingram
# Date: 12/7/2023
# Email: ingramca@oregonstate.edu 
#
#   SOURCES:
#       The following was inspired by https://docs.python.org/3/library/socket.html#socket.socket:
#           constructing a new socket object using socket()
#   
#       The following were inspired by https://www.internalpointers.com/post/making-http-requests-sockets-python:
#           connecting socket to host using socket method connect()
#           sending messages over socket connection using socket method sendall()
#           receiving response using socket method recv()
#
#       The following was inspired by https://www.geeksforgeeks.org/clear-screen-python/
#           os.system('clear') to clear the terminal for visual clarity


import socket
import os

def prep_send_to_server(socket):
    maintain_connection = True

    # get message to send to server
    message_to_server = input("Enter input > ")

    # shut down if prompted, otherwise encode and send a nonempty message <4096 bytes
    if message_to_server == '/q':
        maintain_connection = False

    elif message_to_server == '':
        print("Please try again")
        return prep_send_to_server(socket)
    
    elif len(message_to_server) > 4096:
        print(f"Your message was {len(message_to_server)} characters. Please try again \
              with a shorter message (4096 byte max)")
        return prep_send_to_server(socket)
    
    else:
        maintain_connection = True
    
    return maintain_connection, message_to_server

def receive_from_server(socket):
    maintain_connection = True
    # receive and decode a message from the server through an established socket
    message_from_server = socket.recv(4096) 
    message_from_server = message_from_server.decode()
    
    # prompt termination if server sent "/q"
    if message_from_server == '/q':
        maintain_connection = False

    return maintain_connection, message_from_server

def shut_down():
    return False, False

def print_rps_instructions():
    print("\nInstructions:")
    print("   -Type /q to quit.")
    print('   -Type R to play rock, P for paper, or S for scissors\n')

def respond_to_rps_request(s):
    #print instructions
    print("\nThe server wants to play a round of rock-paper-scissors!")
    print_rps_instructions()

    # send client move
    client_move = ""
    while client_move.lower() not in ["r","p","s","/q"]:
        client_move = input("Please enter your move (R/P/S): > ")
    s.sendall(client_move.encode())
    
    if client_move == "/q":
        print("Rock-paper-scissors denied. Returning to normal chat mode.\n")
        return

    # get client move
    print("Getting server's move...")
    server_move = s.recv(4096)
    server_move = server_move.decode()

    # print results
    calculate_and_print_rps_results(server_move, client_move)

def initiate_rps(s):
    # print instructions
    print("\nYou have opted to play a round of rock-paper-scissors!")
    print_rps_instructions()

    # get server's move
    print("Waiting for server's move...")
    server_move = s.recv(4096) 
    server_move = server_move.decode()
    if server_move == "/q":
        print("Rock-paper-scissors denied by server. Returning to normal chat mode.\n")
        print("Waiting for server to send a chat...")
        return

    # send client's move
    client_move = ""
    while client_move.lower() not in ["r","p","s","/q"]:
        client_move = input("Please enter your move (R/P/S): > ")
    client_move = client_move.lower()
    s.sendall(client_move.encode())

    calculate_and_print_rps_results(server_move, client_move)

    print("\nReturning to normal chat mode. Waiting for server chat...")

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

def start_client(port):
    os.system('clear')
    # create socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # connect socket to localhost at a given port
        s.connect(('localhost', port))
        print(f"Connected to localhost on port: {port}")
        print("\nInstructions:")
        print("   -Please wait for prompt to input a message to the server.")
        print("   -Type /q to quit.")
        print('   -Type "rps" to play a round of rock-paper-scissors\n')

        still_sending = True
        still_receiving = True

        while still_sending and still_receiving:
            if still_sending:
                still_receiving, outgoing_message = prep_send_to_server(s)
                s.sendall(outgoing_message.encode())

                if outgoing_message == '/q':
                    print("Shutting down!")
                    still_receiving, still_sending = shut_down()
                    break
                if outgoing_message == 'rps':
                    initiate_rps(s)

            if still_receiving:
                still_sending, incoming_message = receive_from_server(s)
                print(f"Server: {incoming_message}")

                if incoming_message == "/q":
                    print("Server requested a disconnection. Goodbye!")
                    still_receiving, still_sending = shut_down()
                    break
                if incoming_message.lower() == "rps":
                    respond_to_rps_request(s)

if __name__ == '__main__':
    PORT = 5599
    start_client(PORT)
