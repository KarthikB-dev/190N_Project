type packet = {
    timestamp: number,
    ethernet: {
        src: string,
        dst: string,
    },
    network: {
        src_ip: string,
        dst_ip: string,
        ttl: number,
        tos: string,
        id: string,
        sum: string,
    },
    transport: {
        protocol: string,
        src_port: string | null,
        dst_port: string | null,
        seq: string | null,
        ack: string | null,
        flags: string | null,
        window: string | null,
        data_length: number,
    }
}
