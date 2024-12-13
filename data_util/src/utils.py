from consts import protocols
import scapy.all as scapy
import dpkt
from dpkt.utils import mac_to_str, inet_to_str, make_dict


def get_protocol_name(proto):
    """Return the name of a protocol based on its numeric value."""
    if proto < len(protocols):
        return protocols[proto]
    return "Unknown"


def parse_http_data(tcp_data):
    return False, False
    try:
        return dpkt.http.Request(tcp_data), "http_request"
    except dpkt.UnpackError:
        try:
            return dpkt.http.Response(tcp_data), "http_response"
        except dpkt.UnpackError:
            return False, False


def read_next_packet_helper(iterable):
    ts, pkt = next(iterable)
    eth = dpkt.ethernet.Ethernet(pkt)  # Get the Ethernet frame
    
    if (
        eth.type != dpkt.ethernet.ETH_TYPE_IP
        and eth.type != dpkt.ethernet.ETH_TYPE_8021Q
    ):  # Ignore non-IP/VLAN packets
        return None

    if eth.type == dpkt.ethernet.ETH_TYPE_8021Q and not isinstance(
        eth.data, dpkt.ip.IP
    ):
        # print(type(eth.data))
        return None

    ip: dpkt.ip.IP = eth.data  # Get the IP packet
    
    http, type = parse_http_data(ip.data.data)

    http = make_dict(http) if http is not False else None

    packet = {
        "timestamp": ts,
        "ethernet": {
            "src": mac_to_str(eth.src),
            "dst": mac_to_str(eth.dst),
        },
        "network": {
            "src_ip": inet_to_str(ip.src),
            "dst_ip": inet_to_str(ip.dst),
            "ttl": ip.ttl,
            "tos": ip.tos,
            "id": ip.id,
            "sum": ip.sum,
        },
        "transport": {
            "protocol": get_protocol_name(ip.p),
            "src_port": ip.data.sport if hasattr(ip.data, "sport") else None,
            "dst_port": ip.data.dport if hasattr(ip.data, "dport") else None,
            "seq": ip.data.seq if hasattr(ip.data, "seq") else None,
            "ack": ip.data.ack if hasattr(ip.data, "ack") else None,
            "flags": ip.data.flags if hasattr(ip.data, "flags") else None,
            "window": ip.data.win if hasattr(ip.data, "win") else None,
            "data_length": len(ip.data.data),
        },
        "application": {
            "data": http,
            "type": type,
        },
    }
    return packet


def read_next_packet(iterable):
    res = None
    while res is None:
        try:
            res = read_next_packet_helper(iterable)
        except StopIteration as e:
            if isinstance(e, StopIteration):
                raise e
            print(f"Error reading packet:", e)
    return res
