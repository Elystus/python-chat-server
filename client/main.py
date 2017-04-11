from __future__ import print_function
import colorama
import socket
import select
import sys

class ChatClient(object):

  def __init__(self, address, port, recv=4096):
    self.server_address = address
    self.server_port = port
    self.client_recv = recv

  def start(self):
    self.socket_setup()
    if self.socket_connect():
      self.client_connected()
      self.client_disconnect()

  def socket_setup(self):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)
    self.client_socket = client_socket

  def socket_connect(self):
    successful_connection = False
    try:
      self.client_socket.connect((self.server_address, self.server_port))
      successful_connection = True
    except Exception as err:
      print('Unable to connect to server. Error: {}'.format(err))
    return successful_connection

  def client_connected(self):
    print('Successful connection to Chat Server!')
    try:
      self.client_listen()
    except KeyboardInterrupt as err:
      pass
    except Exception as err:
      print('Error: {}'.format(err))

  def client_listen(self):
    fd_list = [sys.stdin, self.client_socket]
    self.client_prompt()
    while True:
      readable_sockets, _, _ = select.select(fd_list, [], [])
      for read_socket in readable_sockets:
        if read_socket == self.client_socket:
          self.client_received_message()
          self.client_prompt()
        else:
          self.client_send_message()
          self.client_prompt()

  def client_prompt(self):
    print(colorama.Fore.BLUE + '<YOU>: ' + colorama.Fore.RESET, end='')
    sys.stdout.flush()

  def client_received_message(self):
    data = self.client_socket.recv(self.client_recv)
    if not data:
      print('\nDisconnected from chat server...')
      sys.exit()
    else:
      print('\r' + data.strip())

  def client_send_message(self):
    message = sys.stdin.readline()
    self.client_socket.send(message)


  def client_disconnect(self):
    self.client_socket.close()
    print('\nDisconnected from chat server...')

if __name__ == "__main__":

  if (len(sys.argv) < 3):
    print('Usage : python main.py address port')
    sys.exit()

  host = str(sys.argv[1])
  port = int(sys.argv[2])

  chat_client = ChatClient(host, port)
  chat_client.start()