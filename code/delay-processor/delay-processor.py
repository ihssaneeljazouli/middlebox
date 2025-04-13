import asyncio
from nats.aio.client import Client as NATS
import os, random, subprocess, time
from scapy.all import Ether
import matplotlib.pyplot as plt


# lists to store random delays and RTT values
delays = []
rtt_values = []

# Function to calculate RTT for ping packets
async def ping_rtt(destination_ip):
    ping_cmd = ['ping', '-c', '1', destination_ip]
    start_time = time.time()

    process = await asyncio.create_subprocess_exec(
        *ping_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    end_time = time.time()

    rtt = (end_time - start_time) * 1000  # Convert to milliseconds
    return rtt

# Processor function
async def run():
    nc = NATS()

    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data #.decode()
        print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        packet.show()
        # Publish the received message to outpktsec and outpktinsec after adding a delay
        delay = random.expovariate(1 / 5) / 1e6  # delay in seconds  
        delays.append(delay * 1000)
        print("delay added")


        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)
   
    # Subscribe to inpktsec and inpktinsec topics
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Subscribed to inpktsec and inpktinsec topics")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Disconnecting...")
    finally:
        await nc.close()
        #await calculate_rtt()
        #print("RTT values:", rtt_values)
        #plot_delays()
        #plot_rtt()



async def calculate_rtt():
    for _ in range(10):
        rtt = await ping_rtt("insec")
        rtt_values.append(rtt)


def plot_delays():
    plt.figure()
    plt.plot(delays, label="Random delays")
    plt.xlabel("Packet Number")
    plt.ylabel("Delays (ms)")
    plt.title("Random Delay over Packets")
    plt.legend()
    plt.show()
    plt.savefig("delays.png")

def plot_rtt():
    plt.figure()
    plt.plot(rtt_values, label="RTT (ms)")
    plt.xlabel("Packet Number")
    plt.ylabel("RTT (ms)")
    plt.title("RTT over Packets")
    plt.legend()
    plt.show()
    plt.savefig("rtts.png")


if __name__ == '__main__':
    asyncio.run(run())