import asyncio
from nats.aio.client import Client as NATS
import os, random, subprocess, time
from scapy.all import Ether
import matplotlib.pyplot as plt


# lists to store random delays and RTT values
delays = []
rtt_values = []

# Function to calculate RTT for ping packets
def ping_rtt(destination_ip):
    ping_cmd = ['ping', '-c', '1', destination_ip]
    start_time = time.time()
    subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        #print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        print("Received packet",packet.show())
        # Publish the received message to outpktsec and outpktinsec after adding a delay
        delay = random.expovariate(1 / 5e-6)
        await asyncio.sleep(delay * 1000)  # Convert to milliseconds
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
    except KeyboardInterrupt:
        print("Disconnecting...")
        await nc.close()

    calculate_rtt()
    plot_data()

def calculate_rtt():
    for _ in range(10):  #  10 pings
        rtt = ping_rtt("insec") 
        rtt_values.append(rtt)

def plot_data():
    #plotting the random delays
    plt.plot(delays, label="Random delays")
    plt.xlabel("Packet Number")
    plt.ylabel("Delays (ms)")
    plt.title("Random Delay over Packets")
    plt.legend()

    #plotting rtt
    plt.plot(rtt_values, label="RTT (ms)", color="r")
    plt.xlabel("Packet Number")
    plt.ylabel("RTT (ms)")
    plt.title("RTT over Packets")
    plt.legend()

    plt.show()
if __name__ == '__main__':
    asyncio.run(run())