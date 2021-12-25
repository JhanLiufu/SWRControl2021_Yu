'''
This is a testing for whether data can be successfully written into files and saved
'''
import time

with open('/media/nvme0/Data/clc/data/testfile.txt', 'a') as file:
    while True:
    #for i in range(2000):
        file.write(str(time.time_ns())+"\n")