import trodes_connection as tc
import threading

trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20)
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]

'''
def subscribe_test(client):
    client.receive()
    current_sample = trodes_client.receive()
    current_time = current_sample['systemTimestamp']
    current_data = current_sample['lfpData']
    print('LFP Data at time '+str(current_time)+' is '+str(current_data))


receive_thread = threading.Thread(target=subscribe_test, args=trodes_client)
receive_thread.start()
'''

while True:
    current_sample = trodes_client.receive()
    current_data = current_sample['lfpData']
    print(current_data)

