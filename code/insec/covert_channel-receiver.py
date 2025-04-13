import argparse
import json
import time
from scapy.all import sniff, IP, ICMP

timestamps = []

def packet_callback(packet):
    if ICMP in packet:
        ts = time.time()
        print(f"ICMP packet received at {ts}")
        timestamps.append(ts)

def decode_bits(timestamps, threshold):
    bits = ""
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i - 1]) * 1000  # ms
        print(f"Δt = {delta:.2f} ms")
        if delta < 50:
            continue  # ignore noise 

        bit = '1' if delta > threshold else '0'
        bits += bit
    return bits

def bits_to_string(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    
    config = load_config(args.config)
    threshold = config["threshold"]
    duration = config["capture_duration"]
    

    print("Sniffing...")
    #sniff(filter="icmp", prn=packet_callback, timeout=duration)
    sniff(filter="icmp", iface="eth0", prn=packet_callback, store=0,timeout=duration)

    bitstream = decode_bits(timestamps, threshold)
    message = bits_to_string(bitstream)
    print(f"Decoded bitstream: {bitstream}")
    print(f"Decoded message: {message}")

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    main()
