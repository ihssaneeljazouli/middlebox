import os
import time
import argparse
import json
import asyncio
from scapy.all import IP, ICMP, raw, send
from nats.aio.client import Client as NATS

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def encode_message(message):
    return ''.join(format(ord(c), '08b') for c in message)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    config = load_config(args.config)
    ip = config["receiver_ip"]
    delay_0 = config["delay_0"]
    delay_1 = config["delay_1"]
    message = config["message"]

    binary = encode_message(message)
    print(f"Sending: {message} → {binary}")

    # Connect to NATS
    nc = NATS()
    await nc.connect(os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222"))

    prev = time.time()
    for bit in binary:
        now = time.time()
        print(f"Bit: {bit}, Δt = {(now - prev)*1000:.2f} ms")
        prev = now

        pkt = IP(dst=ip) / ICMP()

        # Send actual packet on the network
        send(pkt, verbose=0)

        # Also publish it to NATS for the detector
        await nc.publish("inpktsec", raw(pkt))

        # Delay based on bit
        delay = delay_1 if bit == '1' else delay_0
        await asyncio.sleep(delay / 1000.0)

    # Final packet to close the stream
    pkt = IP(dst=ip) / ICMP()
    send(pkt, verbose=0)
    await nc.publish("inpktsec", raw(pkt))
    await nc.drain()

if __name__ == "__main__":
    asyncio.run(main())
