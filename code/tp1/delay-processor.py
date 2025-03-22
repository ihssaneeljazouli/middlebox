import asyncio
import os
import random
from nats.aio.client import Client as NATS
from scapy.all import Ether

def get_nats_url():
    return os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")

async def run():
    nc = NATS()
    await nc.connect(get_nats_url())

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data
        packet = Ether(data)
        print(packet.show())

        # Introduce a random delay before forwarding
        delay = random.uniform(10, 100) / 1000  # Convert ms to seconds
        await asyncio.sleep(delay)
        print(f"Added delay: {delay * 1000:.2f} ms")

        # Publish the processed packet to the appropriate topic
        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        elif subject == "inpktinsec":
            await nc.publish("outpktsec", msg.data)

    # Subscribe to inpktsec and inpktinsec topics
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Processor with random delay started, listening for frames...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        await nc.close()

if __name__ == '__main__':
    asyncio.run(run())
