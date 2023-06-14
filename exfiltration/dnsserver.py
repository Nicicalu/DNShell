import dns.message
import dns.rcode
import dns.resolver
import dns.query
import socketserver

class DNSServer(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        # Parse the DNS query
        query = dns.message.from_wire(data)

        # Log the DNS query
        self.log_dns_query(query, self.client_address[0], self.client_address[1])

        # Generate a DNS response
        response = self.generate_dns_response(query)

        # Send the DNS response back to the client
        socket.sendto(response.to_wire(), self.client_address)

    def log_dns_query(self, query, client_ip, client_port):
        # Implement your own logic to log the DNS query
        # You can extract relevant information from the query object
        # For simplicity, we'll just print the query details to the console

        print(f'Incoming DNS query from {client_ip}:{client_port}')
        print('Questions:')
        for question in query.question:
            print(question)

    def generate_dns_response(self, query):
        # Implement your own logic to generate a DNS response
        # You can use dnspython's resolver to query an authoritative DNS server for the answer
        # For demonstration purposes, we'll return a dummy response

        response = dns.message.make_response(query)
        response.set_rcode(dns.rcode.NOERROR)
        response.answer.append(dns.rrset.from_text('example.com. 300 IN A 192.0.2.1'))

        return response

# Create a UDP server and bind it to a specific IP address and port
server = socketserver.UDPServer(('0.0.0.0', 53), DNSServer)

# Start the DNS server
server.serve_forever()
