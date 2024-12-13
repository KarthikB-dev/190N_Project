import pyshark
import multiprocessing
import time
from zheli import parse_rec, records, parse_rec_dry
import pandas as pd

from multiprocessing import Process, Value


class QuickParse:
    def __init__(self, output_queue: multiprocessing.Queue, id=0, notifier=None):
        self.output_queue = output_queue
        self.process_queue = multiprocessing.Queue()
        self.processed = 0
        self.accepted = 0
        self.id = id
        self.notifier = notifier

        self.process = None

    def add_packet(self, binary_packet):
        if self.process_queue.qsize() > 100 and not self.process:
            print(f"Starting process {self.id}")
            self.process = multiprocessing.Process(target=self.parse_in_process)
            self.process.start()

        self.accepted += 1
        self.process_queue.put(binary_packet)

    def parse_in_process(self):
        cap = pyshark.InMemCapture()
        while True:
            # if output queue is full, wait
            while self.output_queue.qsize() > 500000:
                time.sleep(0.1)
            # Exec
            packet = self.process_queue.get()
            if packet is None:  # Sentinel value to signal process termination
                print(f"Process {self.id} received termination signal.")
                break
            try:
                res = cap.parse_packets([packet])[0]
                packed = parse_rec_dry(res)
                self.output_queue.put(packed)
            except Exception as e:
                print(f"Error parsing packet in process {self.id}: {e}")
                continue
            self.processed += 1
        print(f"Process {self.id} finished")
        with self.notifier.get_lock():
            self.notifier.value += 1

    def join(self):
        if self.process and self.process.is_alive():
            print(f"Joining process {self.id} - Alive: {self.process.is_alive()}")
            self.process.join(timeout=5)  # Wait up to 5 seconds
            if self.process.is_alive():
                print(f"Process {self.id} did not exit. Terminating.")
                self.process.terminate()
                self.process.join()
            print(f"Process {self.id} joined successfully.")


def cap(input_pcap):
    THREADS = 16
    with open(input_pcap, "rb") as file:
        magic_number = file.read(4)
        major_version = file.read(2)
        minor_version = file.read(2)
        reserved1 = file.read(4)
        reserved2 = file.read(4)
        snaplen = file.read(4)
        network = file.read(4)
        print(f'Pcap Magic number: {int.from_bytes(magic_number, byteorder="little")}')
        print(
            f'Pcap Version: {int.from_bytes(major_version, byteorder="little")}.{int.from_bytes(minor_version, byteorder="little")}'
        )

        output_queue = multiprocessing.Queue()
        notifier = multiprocessing.Value("i", 0)
        quick_parsers = [QuickParse(output_queue, _, notifier) for _ in range(THREADS)]
        count = 0

        while True:
            if count > 100000000:  # For testing, limit the number of packets
                break
            print(count, end="\r")
            ts = file.read(4)
            if not ts:
                break
            tsm = file.read(4)
            capl = file.read(4)
            oril = file.read(4)
            packet = file.read(int.from_bytes(capl, byteorder="little"))
            wholepkt = ts + tsm + capl + oril + packet

            quick_parsers[count % THREADS].add_packet(packet)
            count += 1

        print("\nFinished reading pcap file.")

        # Signal all processes to terminate
        for parser in quick_parsers:
            # print(f"Sending termination signal to process {parser.id}")
            parser.process_queue.put(None)

        print("Waiting for all processes to finish...")
        
        output_list = []
        while True:
            with notifier.get_lock():
                if notifier.value == THREADS:
                    break
            print(f"Waiting for {THREADS - notifier.value} processes to finish... Output recorded: {len(output_list)}, Queue size: {output_queue.qsize()}")
            while output_queue.qsize() > 1000:
                if(len(output_list) % 100 == 0):
                    print(f"Output recorded: {len(output_list)}, Queue size: {output_queue.qsize()}, Recorded Percentage: {len(output_list) / count * 100:.2f}%, Queue Percentage: {output_queue.qsize() / count * 100:.2f}%", end='\r')
                output_list.append(output_queue.get())
                
        return output_list

def save(l, output_csv):
    df = pd.DataFrame(l)
    df.to_csv(output_csv, index=False)
    print(f"Extraction complete. Features saved to {output_csv}.")

if __name__ == "__main__":
    input_pcap = "../data/lan.pcap"
    parsed = cap(input_pcap)
    print("PARSE OK", len(parsed))
    save(parsed, "../data/more_output_lan.csv")
