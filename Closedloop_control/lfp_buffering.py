"""""""""
Written by Mengzhan Liufu at Yu Lab, the University of Chicago, November 2021
"""""""""
import time

channel_id = 0


def input_channel_id():
    global channel_id
    channel_id = input("Input the index (not it's name) of the nTrode channel to listen to:")
    print('Listening to channel '+str(channel_id))


def lfp_buffering(client, buffer, buffer_size):
    """
    Receive lfp data package from trodes server and update the lfp buffer of length buffer_size
    :param client: trodes client object
    :param buffer: the real-time updating buffer queue
    :param buffer_size: the length of buffers for real-time processing
    """
    counter = 0
    while True:
        current_sample = client.receive()
        current_time = current_sample['systemTimestamp']
        current_data = current_sample['lfpData']
        buffer.append(current_data[channel_id])

        if counter < buffer_size:
            counter = counter + 1
            continue

        buffer.popleft()  # discards the least recent data point
        #print(current_data)
        #print('Buffer updated at timestamp '+str(time.time_ns()))