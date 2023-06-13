import dns.message
import dns.server

class DNSServer(dns.server.BaseServer):
    def handle_request(self, message, address):
        # Log the incoming DNS query
        self.log_dns_query(message, address)

        # Generate a DNS response (dummy response for demonstration purposes)
        response = dns.message.make_response(message)
        response.answer.append(dns.rrset.from_text('example.com.', 300, dns.rdataclass.IN, dns.rdatatype.A, '192.0.2.1'))

        # Send the DNS response back to the client
        self.send_response(response, address)

    def log_dns_query(self, message, address):
        # Implement your own logic to log the DNS query
        # You can extract relevant information from the message object
        # For simplicity, we'll just print the query details to the console

        print(f'Incoming DNS query from {address[0]}:{address[1]}')
        print('Questions:')
        for question in message.question:
            print(question)

# Create an instance of the DNS server
server = DNSServer(listen_ip='0.0.0.0', listen_port=53)

# Start the DNS server
server.start_thread()

try:
    # Keep the server running until interrupted
    while True:
        pass
except KeyboardInterrupt:
    pass

# Stop the DNS server
server.stop()
