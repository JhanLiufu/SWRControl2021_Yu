import time
import numpy as np


def timestamp_sync(client, duration):
    trodes_localtime = []
    trodes_systemtime = []
    local_systemtime = []

    for i in range(duration):
        initial_sample = client.receive()
        trodes_localtime.append(initial_sample['localTimestamp'])
        trodes_systemtime.append(initial_sample['systemTimestamp'])
        local_systemtime.append((time.time_ns()))

    system_dif = []
    for i in range(1, len(trodes_systemtime)):
        system_dif.append(trodes_systemtime[i]-trodes_systemtime[i-1])
    '''
    How many nanoseconds do 20 sample counts correspond to. Only has access to firsttimestamp (of recording),
    so we need to convert sample count to trodes unix time
    '''
    avg_systemdif = np.mean(system_dif)

    systemPC_dif = []
    for i in range(0, len(trodes_systemtime)):
        systemPC_dif.append(local_systemtime[i]-trodes_systemtime[i])
    '''
    by how many nanoseconds the PC unix time is behind trodes unix time
    the time difference includes inherent difference and time needed to run time_ns(), both of which
    also happen in real time
    '''
    avg_systemPCdif = np.mean(systemPC_dif)

    return avg_systemPCdif, avg_systemdif
