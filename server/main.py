import colorama
import socket
import select
import sys

class ChatServer(object):

  def __init__(self, server_address, server_port=2424, recv_buffer=4096):
    self.server_address = server_address
    self.server_port = server_port
    self.recv_buffer = recv_buffer
    self.client_list = []
    self.client_names = {}

  def start(self):
    self.socket_setup()
    self.socket_wait()
    self.socket_shutdown()

  def socket_setup(self):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((self.server_address, self.server_port))
    server_socket.listen(10)
    self.server_socket = server_socket
    self.client_list.append(server_socket)

  def socket_wait(self):
    try:
      self.socket_listen()
    except KeyboardInterrupt as err:
      pass
    except Exception as err:
      print 'Error: {}'.format(err)

  def socket_listen(self):
    print 'Server listening on {}:{}...'.format(self.server_address, self.server_port)
    while True:
      read_sockets, _, _ = select.select(self.client_list, [], [])
      for readable_socket in read_sockets:
        if readable_socket == self.server_socket:
          self.socket_add_user()
        elif not self.client_names.get(readable_socket):
          self.socket_set_user(readable_socket)
        else:
          self.socket_process_message(readable_socket)

  def socket_add_user(self):
    client_socket, address = self.server_socket.accept()
    print 'New connection from {}:{}'.format(address[0], address[1])
    self.client_list.append(client_socket)
    self.socket_message_send(client_socket, colorama.Fore.LIGHTMAGENTA_EX + '[SERVER MESSAGE]' + colorama.Fore.RESET + ' Provide a username: ')

  def socket_set_user(self, client_socket):
    try:
      data = client_socket.recv(self.recv_buffer).strip()
      if data:
        self.socket_broadcast(self.server_socket, colorama.Fore.LIGHTMAGENTA_EX + '[SERVER BROADCAST]' + colorama.Fore.RESET + ' User {} connected!'.format(data))
        self.client_names[client_socket] = data
      else:
        self.socket_message_send(client_socket, colorama.Fore.LIGHTMAGENTA_EX + '[SERVER MESSAGE]' + colorama.Fore.RESET + ' Provide a username: ')
    except:
      self.socket_remove_user(client_socket)

  def socket_message_send(self, client_socket, message):
    try:
      client_socket.send(message)
    except:
      self.socket_remove_user(client_socket)

  def socket_broadcast(self, talking_socket, message):
    print message
    for client_socket in self.client_list:
      if client_socket != talking_socket and client_socket != self.server_socket:
        self.socket_message_send(client_socket, message)

  def socket_remove_user(self, client_socket):
    username = self.client_names.get(client_socket)
    self.client_list.remove(client_socket)
    if username:
      del self.client_names[client_socket]
      self.socket_broadcast(self.server_socket, colorama.Fore.LIGHTMAGENTA_EX + '[SERVER BROADCAST]' + colorama.Fore.RESET + ' User {} disconnected...'.format(username))
    client_socket.close()

  def socket_process_message(self, client_socket):
    try:
      data = client_socket.recv(self.recv_buffer).strip()
      if len(data) > 1:
        message = colorama.Fore.GREEN + '<{}>:'.format(self.client_names.get(client_socket)) + \
                  colorama.Fore.RESET + ' {}'.format(data)
        self.socket_broadcast(client_socket, message)
      elif not data:
        self.socket_remove_user(client_socket)
    except:
      self.socket_remove_user(client_socket)

  def socket_shutdown(self):
    self.socket_broadcast(self.server_socket, colorama.Fore.LIGHTMAGENTA_EX + '[SERVER BROADCAST]' + colorama.Fore.RESET + ' Server shutting down. All users will be disconnected.')
    self.server_socket.shutdown(socket.SHUT_RDWR)

if __name__ == "__main__":

  if (len(sys.argv) < 3):
    print 'Usage : python main.py address port'
    sys.exit()

  host = str(sys.argv[1])
  port = int(sys.argv[2])

  chat_server = ChatServer(host, port)
  chat_server.start()