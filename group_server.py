import socket
import sys
import hashlib
# CONTRACT
# start_server : string number -> socket
# Takes a hostname and port number, and returns a socket
# that is ready to listen for requests
def start_server (host, port):
  server_address = (host, port)
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(server_address)
  sock.listen(1)
  return sock
# CONTRACT
# get_message : socket -> string
# Takes a socket and loops until it receives a complete message
# from a client. Returns the string we were sent.
# No error handling whatsoever.
def get_message (sock):
  chars = []
  connection, client_address = sock.accept()
  print ("Connection from [{0}]".format(client_address))
  try:
    while True:
      char = connection.recv(1)
      if char == b'\0':
        break
      if char == b'':
        break
      else:
        # print("Appending {0}".format(char))
        chars.append(char.decode("utf-8") )
  finally:
    return (''.join(chars), connection)
# CONTRACT
# socket -> boolean
# Shuts down the socket we're listening on.
def stop_server (sock):
  return sock.close()
# CONTRACT 
# string -> string
# takes a string input and creates a specific string returnable only 
# by this algorithm using the hashing library
def checksum (checkmsg):
  print ("This is the word the check sum sees") #this is being used to prevent 
  print (checkmsg) #any errors and make sure the checksum sees the right string
  hash_md5 = hashlib.md5()
  hash_md5.update(checkmsg.encode('utf-8'))
  print(hash_md5.hexdigest())
  return hash_md5.hexdigest()
# DATA STRUCTURES
# The structures for your server should be defined and documented here.
# SERVER IMPLEMENTATION
# The implementation of your server should go here.
UP  = {}  # username-password dictionary (username key)
MBX = {}
last = {} # holds the last message sent to the username (username key)
IMQ = []
# CONTRACT
def handle_message (msg):
  clientmsg = msg.split(" ")[:-1]
  print ("this is the client msg") #these two lines are used to identify what the
  print (clientmsg)  #user wants to have sent to the server
  checksumclient = (msg.split(" ")[-1]) #this seperates the checksum the client
  print ("this is the check sum they sent") #sent to the server and prints it out
  print (checksumclient) # the print is only here to help with errors
  clientjoin = " ".join(clientmsg) #after making the string into a list we combine it together
  msgchecksum = checksum(clientjoin) #perform the checksum on the msg
  print ("this is the check sum we get") #these two lines print the checksum we got
  print (msgchecksum)
  if msgchecksum == checksumclient: #checks to see if the checksums match before
    print ("WOOHOO")                  #proceeding with the handle msg
    msg = clientjoin #msg was the original string used for the rest of the code
# it seemed easier to set it equal to clientjoin(same without the checksum)
# than to change every instance of msg to clientjoin
    if "DUMP" in msg:
      username = msg.split(" ")[1]
      if username in MBX:
          print(MBX)
          print(IMQ)
          print(UP)
          return ("OK", "Dumped.", username)
    #usernames have been added to each of the handle msg protocols
    #this is so that we can save the last msg being sent to the username
    elif "REGISTER" in msg:
    # seperates the username and password
      username = msg.split(" ")[1]
      password = msg.split(" ")[2]
      if username not in MBX:
          MBX[username] = [] #creates a spot for the username in the dictionaries
          print ("MBX : {0}".format(MBX))
          UP[username] = [password]
          print ("UP : {0}".format(UP))
          return ("OK", "Registered.", username)
      else:
          return ("KO", "Already Registered", username)
    elif "MESSAGE" in msg:
          username = msg.split(" ")[1]
          password =[msg.split(" ")[2]] #used because it will match what comes out of the UP dictionary
          receipient = msg.split(" ")[3]
          print (username, password, receipient, UP[username])
          if username in UP:
             if UP[username] == password:
                if receipient in UP:
               # Get the content; slice everything after
               # the word MESSAGE
                  content = msg.split(" ")[4:]
                 # Put the content back together, and put
                # it on the incoming message queue.
                  MBX[receipient].insert(0, " ".join(content))
                  return ("OK", "Sent message.", username)
                else:
                    return ("KO", "receipient not registered", username)
             else:
                 return ("KO", "Invalid username or password", username)
          else:
              return ("KO", "username not registered", username)
    elif "COUNT" in msg:
      username = msg.split(" ")[1]
      return ("SEND", "COUNTED {0}".format(len(MBX[username])), username)
    elif "DELMSG" in msg:
      username = msg.split(" ")[1]
      password =[msg.split(" ")[2]]
      if username in UP:
        if UP[username] == password:
          MBX[username].pop(0)
          return ("OK", "Message deleted.", username)
        else:
          return ("KO", "Invalid username or password", username)
      else:
        return ("KO", "username not registered", username)
    elif "RESEND" in msg: #this takes place if the client did not recieve the msg 
      username = msg.split(" ")[1]
      if username in last:
        lastmsg = last[username]
        return ("SEND", lastmsg, username)
      else:
        return ("KO", "Username was not sent a message", username)
    elif "GETMSG" in msg:
      username = msg.split(" ")[1]
      password =[msg.split(" ")[2]]
      if username in UP:
        if UP[username] == password:
          first = MBX[username][0]
          print ("First message:\n---\n{0}\n---\n".format(first) )
          return ("SEND", first, username)
        else:
          return ("KO", "Invalid username or password", username)
      else:
        return ("KO", "username not registered", username)
    else:
      print("NO HANDLER FOR CLIENT MESSAGE: [{0}]".format(msg))
      return ("KO", "No handler found for client message.", username)
  else: # this occurs when the checksums do not match
    username = msg.split(" ")[1]
    return("SEND", "RETRY", username) #we send out a retry for the client
if __name__ == "__main__":
  # Check if the user provided all of the 
  # arguments. The script name counts
  # as one of the elements, so we need at 
  # least three, not fewer.
  if len(sys.argv) < 3:
    print ("Usage: ")
    print (" python server.py <host> <port>")
    print (" e.g. python server.py localhost 8888")
    print
    sys.exit()
  host = sys.argv[1]
  port = int(sys.argv[2])
  sock = start_server(host, port)
  print("Running server on host [{0}] and port [{1}]".format(host, port))
  RUNNING = True
  while RUNNING:
    message, conn = get_message(sock)
    print("MESSAGE: [{0}]".format(message))
    result, msg, user = handle_message(message) #the handle_message now also 
    #returns a username to save incase of a retry
    print ("Result: {0}\nMessage: {1}\n".format(result, msg))
    if result == "OK":
      last[user] = result #we first save the msg before we send it out
      mychecksum = str(checksum(result)) #caculate the checksum
      result += " " #add a space and the value we determined before sending
      result += mychecksum
      conn.sendall(bytes("{0}\0".format(result)))
    elif result == "SEND":
      last[user] = msg #save the msg before sending
      mychecksum = str(checksum(msg)) #determine the checksum
      msg += " " #add a space and the checksum before sending it out
      msg += mychecksum
      conn.sendall(bytes("{0}\0".format(msg)))
    else:
      print("'else' reached.")
      RUNNING = False
    conn.close()
  stop_server(sock)
