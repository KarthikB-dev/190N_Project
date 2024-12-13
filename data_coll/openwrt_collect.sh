# Directory to store tcpdump files
OUTPUT_DIR="/root/tcpdump"
mkdir -p "$OUTPUT_DIR"

# Duration for each tcpdump file (in seconds) before rolling over to a new file
DURATION=3600  # Example: 1 hour

# List all interfaces except the loopback and remove any "@" symbols from names
interfaces=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | sed 's/@.*//')

# Start tcpdump for each interface
for interface in $interfaces; do
    # Run tcpdump in the background, rotating files every $DURATION seconds
    tcpdump -i "$interface" -w "$OUTPUT_DIR/${interface}_%Y-%m-%d_%H-%M-%S.pcap" -G "$DURATION" -Z root &
    echo "Started tcpdump on interface $interface, saving to $OUTPUT_DIR"
done

# Wait for all background processes (tcpdump instances) to finish
wait