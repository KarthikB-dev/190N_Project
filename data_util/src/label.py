import os
import sys
import scapy.all as scapy
import dpkt
from dpkt.utils import mac_to_str, inet_to_str, make_dict
from utils import read_next_packet

## Now this thingy only works for Layer 3

wanData = "eth0_2024-11-09_07-12-27"
lanData = [
    "eth1_2024-11-09_07-12-27",
    "eth2_2024-11-09_07-12-27",
    "eth3_2024-11-09_07-12-27",
    "eth3.1921_2024-11-09_07-12-27",
    "VLAN10_2024-11-09_07-12-27",
    "VLAN20_2024-11-09_07-12-27",
    "VLAN30_2024-11-09_07-12-27",
    "VLAN100_2024-11-09_07-12-27",
]

output = "output.csv"

# Open WAN interface pcap file
wan_pcap_stream = open(f"../data/{wanData}.pcap", "rb")
wan_iter = dpkt.pcap.Reader(wan_pcap_stream)


# Open LAN interface pcap files
lan_pcap_streams = [open(f"../data/{lan}.pcap", "rb") for lan in lanData]
lan_iters = [dpkt.pcap.Reader(lan_pcap_stream) for lan_pcap_stream in lan_pcap_streams]

# Open output file
output_file = open(f"../data/{output}", "w")

output_file.write(
    "timestamp,label,src_ip,src_port,dst_ip,dst_port,ttl,tos,id,sum,protocol,seq,ack,flags,window,data_length\n"
)

wan_buffer = []
lan_buffer = []


def fill_wan_buffer(to_ts):
    while True:
        try:
            packet = read_next_packet(wan_iter)
            wan_buffer.append(packet)
            if packet["timestamp"] > to_ts:
                break
        except StopIteration:
            print("End of WAN pcap file")
            break


def fill_lan_buffer(to_ts):
    for lan_iter in lan_iters:
        while True:
            try:
                packet = read_next_packet(lan_iter)
                if packet["network"]["src_ip"].startswith("10.") and packet["network"][
                    "dst_ip"
                ].startswith(
                    "10."
                ):  # Ignore LAN-to-LAN traffic
                    continue
                lan_buffer.append(packet)
                if packet["timestamp"] > to_ts:
                    break
            except StopIteration:
                print("End of LAN pcap file")
                lan_iters.remove(lan_iter)
                break
    # Sort the LAN buffer by timestamp
    lan_buffer.sort(key=lambda x: x["timestamp"])


def match_packets_in_buffers():
    global wan_buffer, lan_buffer
    matched_packets = []
    remove_wan = []
    remove_lan = []
    for i, wan_packet in enumerate(wan_buffer):
        for j, lan_packet in enumerate(lan_buffer):
            if (
                abs(wan_packet["timestamp"] - lan_packet["timestamp"]) < 0.1
                and (
                    (
                        wan_packet["network"]["src_ip"]
                        == lan_packet["network"]["src_ip"]
                        and wan_packet["transport"]["src_port"]
                        == lan_packet["transport"]["src_port"]
                    )
                    or (
                        wan_packet["network"]["dst_ip"]
                        == lan_packet["network"]["dst_ip"]
                        and wan_packet["transport"]["dst_port"]
                        == lan_packet["transport"]["dst_port"]
                    )
                    # or True
                )
                and wan_packet["transport"]["data_length"]
                == lan_packet["transport"]["data_length"]
            ):
                matched_packets.append((wan_packet, lan_packet))
                remove_wan.append(i)
                remove_lan.append(j)
                break
    wan_buffer = [wan_buffer[i] for i in range(len(wan_buffer)) if i not in remove_wan]
    lan_buffer = [lan_buffer[i] for i in range(len(lan_buffer)) if i not in remove_lan]
    return matched_packets


def match(to_ts):
    fill_lan_buffer(to_ts)
    fill_wan_buffer(to_ts)
    match = match_packets_in_buffers()
    for m in match:
        wan, lan = m
        wn = wan["network"]
        ln = lan["network"]
        wt = wan["transport"]
        label = ln["src_ip"] if ln["src_ip"].startswith("10.") else ln["dst_ip"]
        output_file.write(
            f"{wan["timestamp"]},{label},{wn["src_ip"]},{wt["src_port"]},{wn["dst_ip"]},{wt["dst_port"]},{wn["ttl"]},{wn["tos"]},{wn["id"]},{wn["sum"]},{wt["protocol"]},{wt["seq"]},{wt["ack"]},{wt["flags"]},{wt["window"]},{wt["data_length"]}\n"
        )


def main():
    wan_init = read_next_packet(wan_iter)
    wan_buffer.append(wan_init)
    time = int(wan_init["timestamp"]) + 1
    match(time)
    for i in range(100):
        time += 1
        match(time)
    print("UNMATCHED WAN BUFFER")
    for w in wan_buffer:
        print(w)
    print("UNMATCHED LAN BUFFER")
    for l in lan_buffer:
        print(l)
    print("# UNMATCHED WAN BUFFER", len(wan_buffer), file=sys.stderr)
    print("# UNMATCHED LAN BUFFER", len(lan_buffer), file=sys.stderr)


main()
