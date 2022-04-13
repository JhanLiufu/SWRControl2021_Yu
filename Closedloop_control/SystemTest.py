'''
Run this test file before your real session, make sure that you can
stream data and call statescript functions from python
'''
import trodes_connection as tc
import multiprocessing as mp
import time


# def mp_test(a):
#     print('Multiprocessor iteration '+str(a))
#     print(time.time_ns())


trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20, 'lfp')
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]

'''
Stream data from trodes server
'''
for i in range(20):
    current_data = trodes_client.receive()['lfpData']
    print(current_data)

'''
Call statescript function. Do something noticeable, say a buzzer or an LED light.
'''

for i in range(1):
    msg_returned = tc.call_statescript(trodes_hardware, 4)

'''
Test multiprocessing function
'''
# if __name__ == '__main__':
#     test_pool = mp.Pool(mp.cpu_count())
#     for i in range(10):
#         test_pool.apply_async(mp_test, args=[i])
#     test_pool.close()
#     test_pool.join()





