![image](https://github.com/Nicicalu/DNShell/assets/52490746/e8d49789-d7a5-4238-86ae-470a6d96a14e)

# DNS(hell)
DNShell is a command and control (C2) tool that utilizes DNS communication for covert command execution and data exfiltration. It allows a client to establish a connection with a server using DNS queries and responses, enabling communication even in restrictive network environments.

# **Getting Started**


1. Set up the server: Deploy the DNShell server on a publicly accessible system. Start the DNShell `server.py` and input your domain and IP. 

   
   1. Clone this repo and cd into the directory

      ```bash
      git clone https://github.com/Nicicalu/DNShell.git
      cd DNShell
      ```
   2. Install dependencies

      ```bash
      pip3 install -r requirements.txt
      ```
   3. Run the `server.py`

      ```bash
      python3 server.py
      ```
2. Set the NS (Nameserver) record of the domain you want to the IP of this public system.
3. Set up the client: Run the DNShell `server.py` and choose the option to generate the client file.
4. Execute commands: Once the client is connected to the server, send encoded commands from the server to execute on the client system.

# Usage

```
     ______ _   _  _____ _          _ _
    |  _  \ \ | |/  ___| |        | | |
    | | | |  \| |\ `--.| |__   ___| | |
    | | | | . ` | `--. \ '_ \ / _ \ | |
    | |/ /| |\  |/\__/ / | | |  __/ | |
    |___/ \_| \_/\____/|_| |_|\___|_|_|

| ------------------------------------------------------------------------------------------------------|
| When you start DNShell without parameters it let's you choose, what you want to do                    |
| If you need the .ps1 file for the vitcim. Use the "--generate-client" argument                        |
|                                                                                                       |
| Author: Nicolas Caluori                                                                               |
| Github: https://github.com/Nicicalu/dnshell                                                           |
|-------------------------------------------------------------------------------------------------------|

usage: server.py [-h] [--start-server] [--generate-client]

options:
  -h, --help         show this help message and exit
  --start-server     Starts the listener
  --generate-client  Generates the .ps1 client file
```

# How it works

## Server sending commands

The client-server communication in this tool follows a specific pattern to ensure data exchange.

* The server is unable to directly send data to the client. Instead, the client actively retrieves data from the server by periodically performing DNS queries. This approach leverages DNS as a covert channel for communication.
* When the client initiates a DNS query and there are no new commands to execute, the server responds by indicating that there is no corresponding DNS record available. This serves as a signal to the client that there are no pending commands to be executed. 
* On the server side, when a user inputs a command, the server waits for the next DNS query from the client. Once the client performs the subsequent DNS query, the server responds by including the base64 encoded command within the data section of the TXT record.
* After a successful response, both the client and server increment their “commandcounter”, as specified in the DNS structure. This counter incrementation is necessary because many DNS servers utilize caching mechanisms. Without this counter, if there were no changes in the domain, subsequent DNS queries would be intercepted and answered by the first DNS server in the chain with the same response as the previous query.
* By employing this approach, the tool establishes a covert communication channel, allowing the client to request commands and receive encoded responses from the server through DNS queries, while circumventing potential caching issues in the DNS infrastructure.

### DNS structure

```bash
commandcounter.identifier.domain
```


1. **commandcounter:** This part represents the count of the current DNS answer. It helps in tracking the progress of DNS queries and responses. Everytime a command is sent, this counter is increased.
2. **identifier**: This part serves as an identifier for the specific transmission. It helps associate the transmitted data with the corresponding session. Currently, it’s just the timestamp of the time, where the client script was started.
3. **domain:** This part represents the base domain name used for communication. It acts as the root domain for the entire communication process.

## Client answer

### DNS structure

```bash
data.counter.total.identifier-commandcounter.domain
```


1. **data**: This part represents the data being transmitted. The data is a chunk of the whole, base64 encoded data transmitted.
2. **counter**: This part indicates the sequence number of the current packet being transmitted. It helps in reconstructing the data on the receiving end.
3. **total**: This part indicates the total number of packets into which the data is divided. It provides information about the complete data size and helps in reassembling the chunks on the receiving end.
4. **identifier**: This part serves as an identifier for the specific transmission. It helps associate the transmitted data with the corresponding session. Currently, it’s just the timestamp of the time, where the client script was started.
5. **commandcounter**: This part represents the count of the current DNS answer. It helps in tracking the progress of DNS queries and responses. Everytime a command is sent, this counter is increased.
6. **domain**: This part represents the base domain name used for communication. It acts as the root domain for the entire communication process.

### Data structure

The client always uses JSON to send data to the server. It includes the output of the command, the identifier (code), the commandcounter (counter) and metadata like pwd, user and hostname.

```json
{
  "output": "Output of command..."
  "code": 5124512512
  "counter": 2
  "pwd": "C:\temp"
  "user": "bob"
  "hostname": "workstation01"
}
```
