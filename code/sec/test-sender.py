
import time
import argparse
import json
from scapy.all import IP, ICMP, send

def load_config(path):
    with open(path) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    config = load_config(args.config)
    ip = config["receiver_ip"]

    for _ in range(20):  # send 20 ICMP packets at regular intervals
        pkt = IP(dst=ip)/ICMP()
        send(pkt, verbose=0)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
