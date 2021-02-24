#!/usr/bin/python3
import socket
import sys
import concurrent.futures
import argparse
import ipaddress

class Connect():
    IP = None
    PORT=None
    
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((self.IP, self.PORT))
            if not result:
                print("{}:{} open".format(self.IP, self.PORT))
        return False

def Scan(IP, PORT):
    Connect(IP, PORT).connect()

class Threader(object):
    def __init__(self, HOSTS, PORTS):
        self.ports = PORTS
        self.hosts = HOSTS
        self.workers = len(self.hosts)*len(self.ports)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = []
            if self.hosts:
                for ip in self.hosts:
                    for port in self.ports:
                        futures.append(
                            executor.submit(Scan, ip, port)
                        )

            completed, not_completed = concurrent.futures.wait(futures)
            for result in completed:
                if not result:
                    print("{}".format(result.result()))
        

def Network_Range(NETWORKID):
    networks = []
    for network in NETWORKID:
        hosts = [str(ip) for ip in ipaddress.IPv4Network(network)]
        for host in hosts:
            networks.append(host)
    return networks

def Host_Range(HOSTS):
    return [str(host) for host in HOSTS]

def Port_Range(PORTS):
    (start, end) = PORTS.split('-')
    return range(int(start), int(end))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='MultiScan', description="MultiScan scans hosts for open ports using multi-threading")
    required = parser.add_argument_group('Required')
    required.add_argument('-n', '--network', nargs='+', help='network, use the format [network]/[subnet], ex. 10.10.0.0/25 or 192.168.1.15/32', type=str)
    required.add_argument('-H', '--hosts', nargs='+', help='host list, specific hosts, ex. 10.10.0.5,10.10.0.123', type=str)
    parser.add_argument('-p', '--ports', metavar='PORTS', default=None, 
    help='port list, use the format [start port]-[end port], ex. 20-80. Not specifing uses default range', type=str)
    arguments = parser.parse_args()

    PORT_LIST = None
    HOST_LIST = None
    network_args = vars(arguments)

    if network_args['network']:
        HOST_LIST = Network_Range(network_args['network'])
    elif network_args['hosts']:
        HOST_LIST = Host_Range(network_args['hosts'])
    else:
        parser.error('Invalid network arguments!')
    if arguments.ports:
        PORT_LIST = Port_Range(arguments.ports)
    else:
        PORT_LIST = Port_Range("0-1023")
    
    Threader(HOST_LIST, PORT_LIST)
