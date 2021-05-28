#Satellite rotator for M2 Satellite Array
#Linux version that accepts rigctl commands from gpredict
import socket
import time
import serial
import signal
import pdb

def getdde(connection, azser, elser):
    
    #print("waiting for connection")
    #connection, client_address = sock.accept()
    #print ("Connection from ", client_address)
    az = 0.0
    el = 0.0
    status = 0
    #print ("Received:", rcvdata)
    data = connection.recv(1024).decode('utf-8').split(" ")
    #print ("received", data[0])
    #import pdb;pdb.set_trace()
    if (data[0][0] == 'p'):
        badread = False
	    #Read from the rotor controller
        azser.write("Bin;".encode('utf-8'))
        azstring = azser.read(8)
        try:
            current_az = str(azstring)[4:8].split(';')[0]
        except Exception as e:
            print("azimuth malformed: ", azstring)
            badread = True
        #print(current_az)
        elser.write("Bin;".encode('utf-8'))
        elstring = elser.read(8)
        #print(elstring)
        try:
            current_el = str(elstring)[4:8].split(';')[0]
        except Exception as e:
            print("elevation malformed: ", elstring)
            badread = True
        #print(current_el)
        #pdb.set_trace()
        if (badread == False):
            currentazel = current_az +'\n' +current_el + '\n'
            connection.sendall(bytes(currentazel.encode('utf-8')))
        #connection.sendall(b'2.5')
        status="p"
        print("Rotor Azimuth at : " + current_az + " and Elevation at: " + current_el)
    elif (data[0][0] == 'P'):
        az = float(data[1])  
        el = float(data[2])
        
        print ("Setting azimuth to: " +format(az,'.1f') + " and Elevation to: " + format(el, '.1f'))
        #Set command require a response
        connection.sendall(b'RPRT 0\n')
        status = "P"
    #az = float(data[1].split(":")[1])
    #el = float(data[2].split(":")[1])
        if (el < 0):
            el = 0 #Don't send a negative elevation back
    elif (data[0][0] == 'S'):
        print("Shutdown command received")
        status="S"
    return (az,el, status)
    
def main():
    #Get az el from DDE server
    testing = False #Change to false when in operation
    TCP_IP = "127.0.0.1"
    TCP_PORT = 4534
    #use renaming in /etc/udev/rules.d/10-local.rules
    azcom = '/dev/azimuth'
    elcom = '/dev/elevation'
    baudrate = 9600
    t = 200
    c=0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, TCP_PORT))
    #Setup serial connections.  For the M2, you need one for AZ and one for EL
     
    try:
        azser = serial.Serial(azcom, baudrate, timeout=1)
    except Exception as e:
        print(e)
        print("Failed to open azimuth", azcom)
        azser = 0
    try:
        elser = serial.Serial(elcom, baudrate, timeout=1)
    except Exception as e:
        print(e)
        elser = 0
        print("Failed to open elevation", elcom)
  
    lastaz = 0
    lastel = 0
    sock.listen(1)
    connection, client_address = sock.accept()
    while (c < t):
        #print("Beginning loop")
        azel = getdde(connection, azser, elser)
        status = azel[2]
        #Check to make sure a new az el was set, and make sure it wasn't the same
        #the Status P is important.  I'm not sure we need to check for last el and az.
        if (status == "P" and ((azel[0] != lastaz) or (azel[1] != lastel))):
            lastaz = azel[0]
            lastel = azel[1]
            #print("Azimuth is: ", lastaz)
            #print("Elevation is: ", lastel)
            #Rotor controller only wants 1 digit after the decimal, so format .1f fixes it
            azupdate = "APn" + format(lastaz,'.1f') + "\r;"
            elupdate = "APn" + format(lastel,'.1f') + "\r;"
            print (azupdate)
            print (elupdate)

            if not testing:
                try:
                    azser.write(azupdate.encode('utf-8'))
                    print("azupdate")
                except:
                    print("Failed to write azimuth")
                    import pdb;pdb.set_trace()
                try:
                    elser.write(elupdate.encode('utf-8'))
                    print("elupdate")
                except:
                    print("Failed to write elevation")
            else:
                print ("Testing mode enabled")
        if (azel[2] == "S"):
            print("Shutdown received")
            print("waiting for new connection")
            connection.close()
            connection, client_address = sock.accept()
        #comment out so you can loop forever.
        #c = c + 1
	
if __name__ == '__main__':
    main()
