import os
import time
import argparse
import json
from scapy.all import IP, ICMP, send

host = os.getenv('INSECURENET_HOST_IP')
port = 8888

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def send_icmp_packet(dest_ip):
    pkt = IP(dst=dest_ip)/ICMP()
    send(pkt, verbose=0)
def encode_message(message):
    return ''.join(format(ord(c), '08b') for c in message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    
    config = load_config(args.config)
    ip = config["receiver_ip"]
    delay_0 = config["delay_0"]
    delay_1 = config["delay_1"]
    message = config["message"]
    
    binary_message = encode_message(message)
    print(f"Sending: {message} -> {binary_message}")
    
    prev = time.time()
    for bit in binary_message:
        now = time.time()
        print(f"Bit: {bit}, Δt since last: {(now - prev)*1000:.2f} ms")
        prev = now
        send_icmp_packet(ip)
        delay = delay_1 if bit == '1' else delay_0
        time.sleep(delay / 1000.0)
if __name__ == "__main__":
    main()
