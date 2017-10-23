# Messaging Client
import socket
import sys
import hashlib #this is used for the checksum
import time#this is used for sleep in the error handler
MSGLEN = 1
#saving the last message that we sent in this area, just in case
last = " "
# CONTRACT
# get_message : socket -> string
# Takes a socket and loops until it receives a complete message
# from a client. Returns the string we were sent.
# No error handling whatsoever.
def receive_message (sock):
  chars = []
  try:
    while True:
      char = sock.recv(1)
      if char == b'\0':
        break
      if char == b'':
        break
      else:
        # print("Appending {0}".format(char))
        chars.append(char.decode("utf-8") )
  finally:
    return ''.join(chars)
# CONTRACT 
# string -> string
# takes a string input and creates a specific string returnable only 
# by this algorithm using the hashing library
def checksum (checkmsg):
  print "this is what the checksum sees" #this is used to see what our checksum
  print checkmsg #sees, this is used to help with errors
  hash_md5 = hashlib.md5()
  hash_md5.update(checkmsg.encode('utf-8'))
  print "this is what we get for the checksum"
  print(hash_md5.hexdigest())
  return hash_md5.hexdigest()
def send (msg):
  global last
  last = msg #this saves the msg before it is sent
  print "this is the msg we are sending" #these two lines are used to help with 
  print msg                              #errors
  clientsums = (str(checksum(msg)))#this performs a checksum on the msg
  print "this is the checksum we get for the msg"
  print clientsums #we print it out to make sure we know//for errors
  msg += " " #we add a space and the checksum to the msg before sending
  msg += clientsums
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
  length = sock.send(bytes(msg + "\0"))
  print ("SENT MSG: '{0}'".format(msg))
  print ("CHARACTERS SENT: [{0}]".format(length))
  return sock
def recv (sock):
  response = receive_message(sock)
  servermsg = response.split(" ")[:-1] #we use this to grab the msg the server
  print "this is the servers message" #sent back and then print it out
  print servermsg
  checksumserver = (response.split(" ")[-1]) #we grab the checksum that the server
  print "this is the check sum they sent" #caculated and print it out
  print checksumserver
  serverjoin = " ".join(servermsg) # we combine the msg back together
  msgchecksum = checksum(serverjoin)# then perform a checksum on the msg
  print "this is teh check sum we get" # and print out what it returns
  print msgchecksum
  if msgchecksum == checksumserver: # we check to make sure the checksums match
    print "Checksum pass" #we explain that the checksum passed
    if servermsg[0] == "RETRY": #if they do we check to see if they wanted us to
      sock.close()
      return "RETRY" #resend our last msg, if so we return retry
    sock.close()
    return True #if everything worked out well we return True
  else:
    print "checksum fail resending" #if the checksum check failed we want to 
    sock.close()                    #return false
    return False
def send_recv (msg):
  statement = recv(send(msg))# we call our operations and get a response from recv
  print "this is the last msg the client has saved"#printing last for error reasons
  print last
  if statement == True: #if it is true there is no apparent errors
        pass# things have went well, just keep going
  elif statement == "RETRY":#if we get retry, the server didn't like our msg
        send_recv(last) #in this case we now retry to send the last msg
  else:
        print msg #if it returns false/anything else, we ask them to RESEND
        username = msg.split(" ")[1]
        resendmsg = "RESEND" + " " + username
        send_recv(resendmsg)
if __name__ == "__main__":
  # Check if the user provided all of the 
  # arguments. The script name counts
  # as one of the elements, so we need at 
  # least three, not fewer.
  if len(sys.argv) < 3:
    print ("Usage:")
    print (" python client.py <host> <port>")
    print (" For example:")
    print (" python client.py localhost 8888")
    print
    sys.exit()
  HOST = sys.argv[1]
  PORT = int(sys.argv[2])
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
  length = sock.send(bytes("REGISTER <random1> password1 0b9c650d354aeb79307fd49d8b722a37\0"))#
  #this is an inserted checksum ^^^, it does not use send_recv so it needs to be right
  print ("CHARACTERS SENT: [{0}]".format(length))
  response = receive_message(sock)
  print("RESPONSE: [{0}]".format(response))
  sock.close()
  # I don't want to copy paste everything above.
  # So, I put it in a function or two.
  # We wrapped our functionality inside of these function calls
  # this allows us to use send_recv to include all of the changes we want to add
  try:
    send_recv("REGISTER <random2> password2")
    send_recv("REGISTER <jadudm> secret")
    send_recv("MESSAGE <random1> password1 <jadudm> Four score and seven years ago.")
    send_recv("DUMP <jadudm>")
    send_recv("MESSAGE <random1> password1 <random2> Four score and seven years ago.")
    send_recv("DUMP <jadudm>")
    send_recv("GETMSG <jadudm> secret")
    send_recv("DUMP <jadudm>")
  except:
    print("Connection Refused!! Exiting ...............")
    time.sleep(3)
    sys.exit()
