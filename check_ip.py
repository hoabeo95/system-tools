import socket

hostname = socket.gethostname()
ip_addresses = [addrinfo[4][0] for addrinfo in socket.getaddrinfo(hostname, None)]

print(f"The IP addresses of {hostname} are: {', '.join(ip_addresses)}")
