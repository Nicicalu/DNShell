import subprocess
import re
import sys

logfile = "../bind/log/query.log"

# Define a regular expression pattern to match the log line
pattern = r"queries: client @\S+ (\d+\.\d+\.\d+\.\d+)#\d+ \((\S+)\): query: (\S+) (\S+) (\S+) -\S+\(\d+\)D \(\S+\)"

# Print out the encoding of the log file and the regular expression pattern
print(f"Log file encoding: {sys.getdefaultencoding()}")
print(f"Pattern encoding: {sys.getdefaultencoding()}")

# Start tailing the log file
p = subprocess.Popen(['tail', '-F', logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Loop through the output of tail
while True:
    line = p.stdout.readline()
    if line:
        # Convert the line to a string using the correct encoding
        line_str = line.decode(sys.getdefaultencoding()).strip()

        # Use the regular expression pattern to extract the relevant information from the log line
        match = re.match(pattern, line_str)
        if match:
            ip_address = match.group(1)
            domain_name = match.group(2)
            query_type = match.group(3)
            query_class = match.group(4)

            # Do something with the extracted information
            print(f"New query arrived from {ip_address} for {domain_name} ({query_type}/{query_class})")
        else:
            print(f"No match {line_str}")
            print(f"Pattern {pattern}")