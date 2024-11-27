# Overview

The purpose of this project is to make educated guesses
about the types of hosts behind a gateway where NAT (Network Address Translation) 
is in use. We plan to apply to some machine learning model to accomplish this.

# What is Network Address Translation?

NAT is a process by which one IP address (typically that of your network gateway) represents
all the hosts in some network. NAT was devised to address the IPv4 address shortage, but it has the ancillary benefit of hiding network hosts from would be attackers.

# How Was Data Collected?

`tcpdump` was run on OpenWRT devices deployed at various locations, chief among them WAN ports. This data consisted of packet headers, timestamps, etc. This data was collected using a Shell script deployed to these devices.
