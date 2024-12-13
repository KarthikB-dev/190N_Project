import pyshark
import pandas as pd
import threading

input_pcap = '../data/wan.pcap'
output_csv = '../data/wan_features.csv'
nat_mapping = {
    '10.114.0.61': 'host1',
    '10.114.0.62': 'host2',
    '10.114.0.63': 'host3',
    '10.114.0.71': 'host4',
    '10.114.0.72': 'host5',
    '10.114.0.73': 'host6'
}

def get_tls_info(pkt):
    """Extract TLS handshake features if present."""
    tls_info = {
        'tls_version': None,
        'tls_handshake_type': None,
        'tls_cipher_suite': None,
        'tls_record_length': None,
        'tls_extensions': None,
        'tls_sni': None
    }
    if hasattr(pkt, 'tls'):
        if hasattr(pkt.tls, 'record_version'):
            tls_info['tls_version'] = pkt.tls.record_version
        if hasattr(pkt.tls, 'handshake_type'):
            tls_info['tls_handshake_type'] = pkt.tls.handshake_type
        if hasattr(pkt.tls, 'handshake_ciphersuite'):
            tls_info['tls_cipher_suite'] = pkt.tls.handshake_ciphersuite
        if hasattr(pkt.tls, 'record_length'):
            tls_info['tls_record_length'] = pkt.tls.record_length
        if hasattr(pkt.tls, 'handshake_extensions_server_name'):
            tls_info['tls_sni'] = pkt.tls.handshake_extensions_server_name
        if hasattr(pkt.tls, 'handshake_extension_type'):
            tls_info['tls_extensions'] = pkt.tls.handshake_extension_type
    return tls_info

def get_basic_ip_info(pkt):
    """Extract basic IP-level features if present."""
    ip_info = {
        'src_ip': None,
        'dst_ip': None,
        'ip_ttl': None,
        'ip_len': None,
        'ip_flags': None,
        'ip_proto': None
    }
    if hasattr(pkt, 'ip'):
        ip_info['src_ip'] = pkt.ip.src
        ip_info['dst_ip'] = pkt.ip.dst
        ip_info['ip_ttl'] = int(pkt.ip.ttl) if hasattr(pkt.ip, 'ttl') else None
        ip_info['ip_len'] = int(pkt.ip.len) if hasattr(pkt.ip, 'len') else None
        ip_info['ip_flags'] = pkt.ip.flags if hasattr(pkt.ip, 'flags') else None
        ip_info['ip_proto'] = pkt.ip.proto if hasattr(pkt.ip, 'proto') else None
    return ip_info

def get_transport_info(pkt):
    """Extract transport-level features (TCP/UDP)."""
    transport_info = {
        'src_port': None,
        'dst_port': None,
        'tcp_flags': None,
        'udp_length': None,
    }

    if hasattr(pkt, 'tcp'):
        transport_info['src_port'] = int(pkt.tcp.srcport) if hasattr(pkt.tcp, 'srcport') else None
        transport_info['dst_port'] = int(pkt.tcp.dstport) if hasattr(pkt.tcp, 'dstport') else None
        transport_info['tcp_flags'] = pkt.tcp.flags if hasattr(pkt.tcp, 'flags') else None

    elif hasattr(pkt, 'udp'):
        transport_info['src_port'] = int(pkt.udp.srcport) if hasattr(pkt.udp, 'srcport') else None
        transport_info['dst_port'] = int(pkt.udp.dstport) if hasattr(pkt.udp, 'dstport') else None
        transport_info['udp_length'] = int(pkt.udp.length) if hasattr(pkt.udp, 'length') else None

    return transport_info

def get_application_info(pkt):
    """Extract application-level features from HTTP, DNS, etc."""
    app_info = {
        'http_host': None,
        'http_uri': None,
        'http_user_agent': None,
        'dns_query_name': None,
        'dns_response_ip': None
    }

    if hasattr(pkt, 'http'):
        if hasattr(pkt.http, 'host'):
            app_info['http_host'] = pkt.http.host
        if hasattr(pkt.http, 'request_uri'):
            app_info['http_uri'] = pkt.http.request_uri
        if hasattr(pkt.http, 'user_agent'):
            app_info['http_user_agent'] = pkt.http.user_agent

    if hasattr(pkt, 'dns'):
        if hasattr(pkt.dns, 'qry_name'):
            app_info['dns_query_name'] = pkt.dns.qry_name
        if hasattr(pkt.dns, 'a'):
            app_info['dns_response_ip'] = pkt.dns.a

    return app_info

def map_to_internal_host(ip_address, mapping):
    """Map internal IP to host label, if it's known (LAN side)."""
    return mapping.get(ip_address, 'unknown')

cap = pyshark.FileCapture(input_pcap, keep_packets=False)
records = []

def parse_rec(pkt):
    try:
        ip_features = get_basic_ip_info(pkt)
        transport_features = get_transport_info(pkt)
        tls_features = get_tls_info(pkt)
        app_features = get_application_info(pkt)

        # On WAN side, these won't match internal NAT IPs.
        # On LAN side, they should.
        internal_host = map_to_internal_host(ip_features['src_ip'], nat_mapping) if ip_features['src_ip'] else 'unknown'

        record = {}
        record.update(ip_features)
        record.update(transport_features)
        record.update(tls_features)
        record.update(app_features)
        record['internal_host_label'] = internal_host

        records.append(record)
    except Exception as e:
        print(f"Error parsing packet: {e}")
        
def parse_rec_dry(pkt):
    try:
        ip_features = get_basic_ip_info(pkt)
        transport_features = get_transport_info(pkt)
        tls_features = get_tls_info(pkt)
        app_features = get_application_info(pkt)

        # On WAN side, these won't match internal NAT IPs.
        # On LAN side, they should.
        internal_host = map_to_internal_host(ip_features['src_ip'], nat_mapping) if ip_features['src_ip'] else 'unknown'

        record = {}
        record.update(ip_features)
        record.update(transport_features)
        record.update(tls_features)
        record.update(app_features)
        record['internal_host_label'] = internal_host

        return record
    except Exception as e:
        print(f"Error parsing packet: {e}")
    
# THREADS = 4
# threads = []
# thread_tasks = [[] for _ in range(THREADS)]
# for i, pkt in enumerate(cap):
#     if i % 1000 == 0:
#         print(f"Processed {i} packets.", end='\r')
#     thread_tasks[i % THREADS].append(pkt)

# print("Starting threads.")
# for i in range(THREADS):
#     t = threading.Thread(target=parse_arr, args=(thread_tasks[i],))
#     threads.append(t)
#     t.start()
    
# for t in threads:
#     t.join()
    
# print("All threads complete.")

# cap.close()

def save():
    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    print(f"Extraction complete. Features saved to {output_csv}.")
