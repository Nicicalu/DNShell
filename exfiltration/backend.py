import subprocess
import re

logfile = "../bind/log/query.log"

# Define a regular expression pattern to match the log line
pattern = r"queries: client @\S+ (\d+\.\d+\.\d+\.\d+)#\d+ \((\S+)\): query: (\S+) (\S+) (\S+) -\S+\(\d+\)D \(\S+\)"

# Start tailing the log file
p = subprocess.Popen(['tail', '-F', logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Loop through the output of tail
while True:
    line = p.stdout.readline()
    if line:
        # Use the regular expression pattern to extract the relevant information from the log line
        match = re.match(pattern, "16-Jun-2023 15:28:08.026 queries: client @0x7f3d18004548 193.135.143.35#56620 (test46.dnshell.programm.zip): query: test46.dnshell.programm.zip IN AAAA -E(0)D (192.168.64.2)")
        if match:
            ip_address = match.group(1)
            domain_name = match.group(2)
            query_type = match.group(3)
            query_class = match.group(4)

            # Do something with the extracted information
            print(f"New query arrived from {ip_address} for {domain_name} ({query_type}/{query_class})")
        else:
            print(f"No match {line.decode()}")