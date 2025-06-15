import asyncio
from nats.aio.client import Client as NATS
import os, time
from scapy.all import Ether
import numpy as np


# === CONFIGURATION ===
# Number of packets to collect before running detection
BATCH_SIZE = 100
# List to store packet arrival timestamps
arrival_times = []


# === FEATURE EXTRACTION ===
def compute_ipd_features(times):
    ipds = np.diff(times)  # Inter-packet delays
    mean_delay = np.mean(ipds)
    std_delay = np.std(ipds)
    spikes = np.sum(np.abs(np.diff(ipds)) > 0.05) #large change in delay (> 0.05s here)
    return mean_delay, std_delay, spikes


# === HEURISTIC DETECTOR ===
def is_covert(mean, std, spikes):
    return std > 0.02 and spikes > 5 # mean is not currently used, but kept for future threshold tuning



# === MAIN PROCESSOR FUNCTION ===
async def run():
    nc = NATS()

    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    print("Subscribed to inpktsec and inpktinsec topics")

    # Define handler function for each received message
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data
        print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        print(packet.show())
        # Log arrival timestamp
        arrival_times.append(time.time())

        # Run detection every BATCH_SIZE packets
        if len(arrival_times) >= BATCH_SIZE:
            mean, std, spikes = compute_ipd_features(arrival_times)
            covert = is_covert(mean, std, spikes)
            print(f"[DETECTOR] mean={mean:.5f}, std={std:.5f}, spikes={spikes} → Covert Detected = {covert}")
            arrival_times.clear()  # Reset for next batch

        # Forward packet to the appropriate topic
        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)

    # Subscribe to both secure and insecure input streams
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Subscribed to inpktsec and inpktinsec topics")


    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        await nc.close()


if __name__ == '__main__':
    asyncio.run(run())
