'''
Code for xArm written by Alex Gillespie
Code for sensor reading provided by Akhil Padmanabha
Last modified: 08/03/2023
'''

from xarm.wrapper import XArmAPI
import os
import serial
import numpy as np
import pickle
import time
''' 
Anything that could require alteration will be marked with 'SPECIFY: ' but everthing else should be consistent
'''

# xArm initialization
arm = XArmAPI("192.168.1.199")
print()
print("setting arm to initial position...")
arm.set_position(338.0, 28.6, 50.1, -15.5, -88.4, -72.5, speed=50, is_radian=False, wait=False)
arm.set_gripper_position(840, wait = False)

# data collection function
def collect_data(container, content, labels, k, i, num_total_its, closed_pos, current_array=None):
    # Serial initialization
    baudrate = 115200

    # TODO
    # SPECIFY: your serial ports for the Teensys
    port1 = '/dev/cu.usbmodem126006401'
    port2 = '/dev/cu.usbmodem126007201'
    serialTeensy_1 = serial.Serial(port=port1, baudrate=baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    serialTeensy_2 = serial.Serial(port=port2, baudrate=baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    count = 0
    buffer1 =  [] # for values of teensy 1
    buffer2 =  [] # for values of teensy 2

    start = time.time()
    serialTeensy_1 = serial.Serial(port1, baudrate)
    serialTeensy_2 = serial.Serial(port2, baudrate)

    # checking on Teensy connections and resetting input buffer
    if serialTeensy_1 is None:
        raise RuntimeError('Serial Port is not found!')
    serialTeensy_1.reset_input_buffer()
    if serialTeensy_2 is None:
        raise RuntimeError('Serial Port is not found!')
    serialTeensy_2.reset_input_buffer()

    flag_first_time = True

    arm.set_gripper_position(closed_pos, wait = False)
    while count<200:
        buffer1.append(serialTeensy_1.read())
        buffer2.append(serialTeensy_2.read())
        # each series of bytes is 17 bytes long, so both the left and right teensy need to be at least 18 bytes long to start reading it
        if len(buffer1) >= 18 and len(buffer2) >= 18:
            # These bytes indicate a new series of sensor values 
            new_line1 = int.from_bytes(buffer1[0], byteorder='little')
            new_line2 = int.from_bytes(buffer1[1],byteorder='little')
            new_line3 = int.from_bytes(buffer1[2],byteorder='little')
            new_line4 = int.from_bytes(buffer2[0], byteorder='little')
            new_line5 = int.from_bytes(buffer2[1],byteorder='little')
            new_line6 = int.from_bytes(buffer2[2],byteorder='little')
            # If all the bytes are 255, the maximum value (3 max bytes in a row for each teensy), that's how we know we're reading the sensor values
            if new_line1 == 255 and new_line2 == 255 and new_line3 == 255 and new_line4 == 255 and new_line5 == 255 and new_line6 == 255:
                # These teensy values store the time at which the values were taken 
                teensy_1_time = int.from_bytes(buffer1[13]+buffer1[14]+buffer1[15]+buffer1[16],byteorder='little')
                teensy_2_time = int.from_bytes(buffer2[13]+buffer2[14]+buffer2[15]+buffer2[16],byteorder='little')
                duration = time.time()-start
                # headers: container, content, labels, iteration, observation (in iteration), python time passed, Teensy time for sensor 1, Teensy time for sensor 2, sensors 1-10
                sensor_vals = np.array([container, content, labels, k, i, num_total_its, count, duration, teensy_1_time, teensy_2_time,
                int.from_bytes(buffer1[3]+buffer1[4],byteorder='little'), 
                int.from_bytes(buffer1[5]+buffer1[6],byteorder='little'), 
                int.from_bytes(buffer1[7]+buffer1[8],byteorder='little'), 
                int.from_bytes(buffer1[9]+buffer1[10],byteorder='little'),
                int.from_bytes(buffer1[11]+buffer1[12],byteorder='little'),
                int.from_bytes(buffer2[3]+buffer2[4],byteorder='little'), 
                int.from_bytes(buffer2[5]+buffer2[6],byteorder='little'), 
                int.from_bytes(buffer2[7]+buffer2[8],byteorder='little'), 
                int.from_bytes(buffer2[9]+buffer2[10],byteorder='little'),
                int.from_bytes(buffer2[11]+buffer2[12],byteorder='little')])
                # if this is the first sensor reading of the iteration, it creates a new array
                if flag_first_time:
                    array_record = sensor_vals
                    flag_first_time = False
                # if this is not the first sensor reading of the iteration, it adds on the values to the existing array
                else:
                    array_record = np.vstack((array_record, sensor_vals))
                    print('Frequency: ', count/(time.time()-start)) # you'll watch these in the terminal to make sure the times all look like they're consistent
                    print('Python time: ', (time.time()-duration))
                    print('Teensy duration 1: ', teensy_1_time-prev_teensy_1_time)
                    print('Teensy duration 2: ', teensy_2_time-prev_teensy_2_time)
                    
                prev_teensy_1_time = teensy_1_time
                prev_teensy_2_time = teensy_2_time
                count +=1
            buffer1.pop(0)
            buffer2.pop(0)
    # prints the number of observations that occurred during that iteration (should be 200)
    print('number of observations: ',count)
    # if this is the first round, you'll return the array you just made
    if current_array is None:
        return array_record
    # if there's already an array for this (if you're working with multiple rounds), you'll add it on to that array and then return 
    else: 
        return np.vstack((current_array, array_record))

# the TOTAL number of iterations will be num_its*num_rounds
num_its = 10 # number of close-hold iterations per round
num_rounds=1 # this allows you to rotate or otherwise alter the container every x number of iterations (where x = num_its)

# TODO specify containers and contents to collect
containers = ['pp', 'glass', 'paper', 'foam', 'ceramic', 'silicon', 'wood', 'pcg', 'pet']
contents = ['water', 'oil', 'honey', 'sugar', 'starch', 'vinegar', 'oats', 'rice', 'lentils']
# TODO directory to send files to after collection
current_dir = 'your directory here'

# All the data will go into a specified directory
direct_label = input('what is the title for the final directory? Example: 1')
new_dir = 'data_collection_'+direct_label
path = os.path.join(current_dir, new_dir)

# OPTIONAL SPECIFY: If you're adding the files to a directory that already exists, comment this out
os.mkdir(path)
os.chdir(current_dir+'/'+new_dir)

arm.set_gripper_speed(600)

labels = 0
# goes through all listen containers
for content in contents:
    print('content is set to '+content)
    # goes through all listed content, sets appropriate content for iteration
    for container in containers:
        # as I mentioned, total iterations is all the iterations in all the rounds
        num_total_its = 0
        # The closed position was obtained by putting an object in the gripper and closing it until it had a good enough grip to manipulate that container
        print('container is set to '+container)
        if container == 'ceramic':
            closed_pos = 680
        elif container == 'pp':
            closed_pos = 640
        elif container == 'paper':
            closed_pos = 645
        elif container == 'foam':
            closed_pos = 645
        elif container == 'silicon':
            closed_pos = 680
        elif container == 'glass':
            closed_pos = 750
        elif container == 'wood':
            closed_pos = 650
        elif container == 'pcg':
            closed_pos = 575
        elif container == 'pet':
            closed_pos = 440
        elif container == 'hdpe':
            closed_pos = 430

        # the open position is relative to the closed position so all containers move approximately 90 mm
        open_pos = closed_pos + 90
        arm.set_gripper_position(840, wait = True)

        # prompt user
        print('\nplace the '+container+' container filled with '+content+' in the gripper')
        place_object = input('press enter to continue.')
        arm.set_gripper_position(open_pos, wait = True)
        for k in range(num_rounds):
            print('round ',k,'of ',num_rounds)
            if k!=0:
                # if it's any round other than the first, you'll be prompted to move/rotate/manipulate the container
                input('alter the state of the container')
            for i in range(num_its):
                print('iteration ',i,'of ',num_its)
                if i == 0:
                    it_array = collect_data(container, content, labels, k, i, num_total_its, closed_pos)
                    flag_first_time = False
                else:
                    it_array = collect_data(container, content, labels,k, i, num_total_its, closed_pos, it_array)
                # because we don't collect data while it opens, we change the speed so it moves faster
                arm.set_gripper_speed(3000)
                arm.set_gripper_position(open_pos, wait = True)
                # after the gripper is open, we change it back
                arm.set_gripper_speed(600)
                num_total_its +=1
            # if it's the first round, initiate a new array
            if k== 0:
                array_record = it_array
            # if it's NOT the first round, add on to a new array
            else:
                array_record = np.vstack((array_record, it_array))
        # dump the pkl file into the directory specified at the beginning
        with open(content+'_'+container+'.pkl','wb') as file:
            pickle.dump(array_record, file)
        labels += 1

# at the end of data collection, reset gripper
arm.set_gripper_position(840, wait = False)
arm.set_position(338.0, 16.7, 215, -15.5, -88.4, -72.5, speed=50, is_radian=False, wait=False)
