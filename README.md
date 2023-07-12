![image](https://github.com/Nicicalu/DNShell/assets/52490746/e8d49789-d7a5-4238-86ae-470a6d96a14e)

DNShell is a Reverse Shell/command and control (C2) tool that utilizes DNS communication for covert command execution and data exfiltration. It allows a client to establish a connection with a server using DNS queries and responses, enabling communication even in restrictive network environments.

### ⚠️ Disclaimer ⚠️
> 
> The DNShell repository and its software are intended for educational and research purposes only. Use of DNShell for illegal activities or unauthorized access is strictly prohibited. The authors and contributors are > not responsible for any misuse or damages caused by the use of this software.

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
2. Set the NS (Nameserver) record of the domain you want to use, to the IP of this public system.
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
| When you start DNShell without parameters it starts the server and waits for incoming connections.    |
| If you need the .ps1 file for the vitcim. Use the "--generate-client" argument                        |
|                                                                                                       |
| Author: Nicolas Caluori                                                                               |
| Github: https://github.com/Nicicalu/dnshell                                                           |
|-------------------------------------------------------------------------------------------------------|

usage: server.py [-h] [--start-server] [--generate-client] [--log-level LOG_LEVEL]

options:
  -h, --help            show this help message and exit
  --start-server        Starts the listener
  --generate-client     Generates the .ps1 client file
  --log-level LOG_LEVEL
                        Set the log level (ERROR=0, INFO=1, DEBUG=2)
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

```
commandcounter.identifier.domain
```

1. **commandcounter:** This part represents the count of the current DNS answer. It helps in tracking the progress of DNS queries and responses. Everytime a command is sent, this counter is increased.
2. **identifier**: This part serves as an identifier for the specific transmission. It helps associate the transmitted data with the corresponding session. Currently, it’s just the timestamp of the time, where the client script was started.
3. **domain:** This part represents the base domain name used for communication. It acts as the root domain for the entire communication process.

Examples:
```
1.1688471883.example.com
2.1688471883.example.com
```

## Client answer

### DNS structure

```
data.counter.total.identifier-commandcounter.domain
```
1. **data**: This part represents the data being transmitted. The data is a chunk of the whole, base32 encoded data transmitted. The padding characters of base 32, `=` are changed to `_` because you can't use `=` in domains
2. **counter**: This part indicates the sequence number of the current packet being transmitted. It helps in reconstructing the data on the receiving end.
3. **total**: This part indicates the total number of packets into which the data is divided. It provides information about the complete data size and helps in reassembling the chunks on the receiving end.
4. **identifier**: This part serves as an identifier for the specific transmission. It helps associate the transmitted data with the corresponding session. Currently, it’s just the timestamp of the time, where the client script was started.
5. **commandcounter**: This part represents the count of the current DNS answer. It helps in tracking the progress of DNS queries and responses. Everytime a command is sent, this counter is increased.
6. **domain**: This part represents the base domain name used for communication. It acts as the root domain for the entire communication process.

Examples:
```
JZSXMZLSEBDW63TOMEQGO2LWMUQHS33VEB2XA___.1.2.1688471883-3.example.com
JBSWY3DPEB3W64TMMQ______.2.2.1688471883-3.example.com
```

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

### Why base32 and not base64?
Base64 can't be used via DNS reliably due to the possibility of 0x20 encoding by some DNS servers (e.g. Google DNS 😡). The 0x20 encoding, also known as "letter case randomization," is a technique employed by some DNS resolvers to provide additional security against DNS spoofing and cache poisoning attacks.

In 0x20 encoding, the resolver modifies the letter case (upper or lower) of the letters in the domain name when performing DNS queries. For example, if a domain name contains the letter 'A,' it may be randomly encoded as either 'A' or 'a' in the DNS query. This encoding helps prevent attackers from easily guessing the correct domain names and increases the difficulty of exploiting DNS vulnerabilities. So `example.com` could be encoded as `eXaMpLe.cOm` or `EXAMple.cOM`. This breaks the base64 encoding, because the letters are not the same anymore and the server can't decode the data.

To ensure reliable data transmission and avoid issues with DNS servers that perform 0x20 encoding, DNShell uses base32 encoding instead of base64. Base32 encoding uses a limited character set consisting of uppercase letters (A-Z) and digits (2-7). This encoding scheme ensures that the transmitted data remains intact and unaffected by DNS server modifications.

By using base32 encoding, DNShell can reliably transmit data over DNS queries, even in environments where DNS servers employ 0x20 encoding. It provides a consistent and covert communication channel between the client and server while maintaining compatibility with a wide range of DNS server configurations.

**More information:**
- https://www.theregister.com/2023/01/19/google_dns_queries/
- https://astrolavos.gatech.edu/articles/increased_dns_resistance.pdf
