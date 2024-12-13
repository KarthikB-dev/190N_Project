import pyshark
import threading
import time


class QuickParse:
    def __init__(self, outputList: list, id=0):
        self.outputList = outputList
        self.processQueue = []
        self.processed = 0
        self.accepted = 0
        self.id = id

        self.thread = None

    def addPacket(self, binary_packet):
        if len(self.processQueue) > 1000 and not self.thread:
            print("starting thread")
            self.thread = threading.Thread(target=self.parseInThread)
            self.thread.start()

        while len(self.processQueue) > 2000:
            time.sleep(0.1)

        self.accepted += 1
        self.processQueue.append(binary_packet)

    def parseInThread(self):
        cap = pyshark.InMemCapture()
        while self.processQueue:
            packet = self.processQueue.pop(0)
            try:
                res = cap.parse_packets([packet])[0]
                self.outputList.append(res)
            except Exception as e:
                print(f"Error parsing packet: {e}")
                continue
            self.processed += 1
            print(
                "Thread",
                self.id,
                "processed",
                self.processed,
                "accepted",
                self.accepted,
            )
        self.thread = None


def cap():
    input_pcap = "../data/wan.pcap"
    THREADS = 8
    with open(input_pcap, "rb") as file:
        magicNumber = file.read(4)
        majorVersion = file.read(2)
        minorVersion = file.read(2)
        reserved1 = file.read(4)
        reserved2 = file.read(4)
        snaplen = file.read(4)
        network = file.read(4)
        print(f'Magic number: {int.from_bytes(magicNumber, byteorder="little")}')
        print(
            f'Version: {int.from_bytes(majorVersion, byteorder="little")}.{int.from_bytes(minorVersion, byteorder="little")}'
        )

        outputList = []
        quickCaps = [QuickParse([], _) for _ in range(THREADS)]
        # cap.set_debug()
        count = 0
        while True:
            print(count, end="\r")
            # Break if eof
            ts = file.read(4)
            if not ts:
                break
            tsm = file.read(4)
            capl = file.read(4)
            oril = file.read(4)
            packet = file.read(int.from_bytes(capl, byteorder="little"))
            wholepkt = ts + tsm + capl + oril + packet

            quickCaps[count % THREADS].addPacket(packet)
            count += 1

        return outputList


parsed = cap()
print("PARSE OK", len(parsed))
print(parsed[0])
