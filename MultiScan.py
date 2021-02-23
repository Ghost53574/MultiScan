#!/usr/bin/python3

# BSD 2-Clause License
# Copyright 2021 Ghost53574 (github.com/Ghost53574)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
            if not sock.connect_ex((self.IP, self.PORT)):
                print("{}:{} is open".format(self.IP, self.PORT))  
            sock.close()
        return False

def Scan(IP, PORT):
    Connect(IP, PORT).connect()

class Threader(object):
    def __init__(self, ip_list, port_list, WORKERS):
        self.workers = int(WORKERS)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = []
            for ip in ip_list:
                for port in port_list:
                    futures.append(
                    executor.submit(Scan, ip, port)
                )

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                try:
                    if result != None:
                        print("{}".format(result))
                except Exception as e:
                    print("Error: {}".format(e))

def Port_Range(ports):
    (start, end) = ports.split('-')
    return range(int(start), int(end))

def Ip_Range(networkid):
    return [str(ip) for ip in ipaddress.IPv4Network(networkid)]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DaScanner scans hosts for open ports using multi-threading")
    parser.add_argument('hosts', help='host list, use the format [network]/[subnet], ex. 10.10.0.0/25', type=str)
    parser.add_argument('-p', '--ports', help='port list, use the format [start port]-[end port], ex. 20-80. Not specifing uses default range', type=str)
    parser.add_argument('-w', '--workers', help='workers, specifiy max threads allowed to spawn', type=int)
    arguments = parser.parse_args()

    PORT_LIST = None
    IP_LIST = None
    WORKERS = None

    if arguments.hosts:
        IP_LIST = Ip_Range(arguments.hosts)
    if arguments.ports:
        PORT_LIST = Port_Range(arguments.ports)
    else:
        PORT_LIST = Port_Range("0-1023")
    if arguments.workers:
        WORKERS = arguments.workers
    else:
        WORKERS = 50

    Threader(IP_LIST, PORT_LIST, WORKERS)