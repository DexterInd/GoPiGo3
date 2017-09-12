import socket
import sys
import easygopigo3
import signal

HOST = "localhost"
PORT = 5002
BUFF_SIZE = 128
try:
    gopigo3 = easygopigo3.EasyGoPiGo3()
    gopigo3.set_speed(100)
    print("GoPiGo3 detected")
except IOError as msg:
    print("GoPiGo3 failure message: " + str(msg))
    sys.exit(1)

try:
    print("creating socket server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
except socket.error as msg:
    print("server error code: " + str(msg[0]))
    print("server failure message: " + str(msg[1]))
    sys.exit(1)
print("bind socket complete on address " + HOST + ":" + str(PORT))
sock.listen(1)
print("listening for client")

def gopigo3_instructions(connection, addr):
    recv_string = connection.recv(BUFF_SIZE).strip().lower()
    while recv_string != "close" and len(recv_string) > 0:
        print("received [" + recv_string + "] command")
        if recv_string == "forward":
            gopigo3.forward()
        elif recv_string == "left":
            gopigo3.left()
        elif recv_string == "right":
            gopigo3.right()
        elif recv_string == "stop":
            gopigo3.stop()
        elif recv_string == "dexleds on":
            gopigo3.open_eyes()
        elif recv_string == "dexleds off":
            gopigo3.close_eyes()
        else:
            print("[" + repr(recv_string) + "] command unknown")

        recv_string = connection.recv(BUFF_SIZE).strip().lower()

    if recv_string == "close":
        print("received [" + recv_string + "] command")
    if len(recv_string) == 0:
        print("received FIN from client")

try:
    connection = None

    while True:
        connection, addr = sock.accept()
        print("connected with " + addr[0] + ":" + str(addr[1]))

        try:
            gopigo3_instructions(connection, addr)
        except socket.error as msg:
            print("Socket error code: " + str(msg[0]))
            print("Socket failure message: " + str(msg[1]))

        connection.close()
        print("disconnected from client")

except (KeyboardInterrupt, SystemExit):
    if connection:
        connection.close()
