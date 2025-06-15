# detector-processor.py
import time
import numpy as np
from scapy.all import sniff, ICMP

BATCH_SIZE = 5
DELAY_SPIKE_THRESHOLD = 0.15
arrival_times = []

def compute_ipd_features(times):
    ipds = np.diff(times)
    mean = np.mean(ipds)
    std = np.std(ipds)
    spikes = np.sum(np.abs(np.diff(ipds)) > DELAY_SPIKE_THRESHOLD)
    return mean, std, spikes

def is_covert(mean, std, spikes):
    return std > 0.05 and spikes >= 3

def handle_packet(pkt):
    if ICMP in pkt:
        now = time.time()
        arrival_times.append(now)
        print(f"📦 ICMP Packet received")

        if len(arrival_times) >= 2:
            ipd = arrival_times[-1] - arrival_times[-2]
            print(f"[⏱️ IPD] Δt = {ipd:.5f}s")

        if len(arrival_times) >= BATCH_SIZE:
            mean, std, spikes = compute_ipd_features(arrival_times)
            print(f"[🔍 DETECTOR] mean={mean:.5f}, std={std:.5f}, spikes={spikes} → Covert Detected = {is_covert(mean,std,spikes)}\n")
            arrival_times.clear()

def main():
    print("📡 Sniffing for ICMP on eth0 inside receiver container...")
    sniff(iface="eth0", filter="icmp", prn=handle_packet, store=False)

if __name__ == "__main__":
    main()
