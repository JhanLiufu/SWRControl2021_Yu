import trodes_connection as tc
import time

trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20)
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]

for i in range(50):
    msg_returned = tc.call_statescript(trodes_hardware, 1)
    print(msg_returned)
    time.sleep(5)

