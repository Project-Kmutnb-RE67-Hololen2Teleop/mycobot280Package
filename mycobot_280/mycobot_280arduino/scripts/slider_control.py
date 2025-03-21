#!/usr/bin/env python2

"""[summary]
This file obtains the joint angle of the manipulator in ROS,
and then sends it directly to the real manipulator using `pymycobot` API.
This file is [slider_control.launch] related script.
Passable parameters:
    port: serial prot string. Defaults is '/dev/ttyUSB0'
    baud: serial prot baudrate. Defaults is 115200.
"""
import time
import math
import rospy
from sensor_msgs.msg import JointState

import pymycobot
from packaging import version
# min low version require
MAX_REQUIRE_VERSION = '3.5.3'
current_verison = pymycobot.__version__
print('current pymycobot library version: {}'.format(current_verison))
if version.parse(current_verison) > version.parse(MAX_REQUIRE_VERSION):
    raise RuntimeError('The version of pymycobot library must be less than {} . The current version is {}. Please downgrade the library version.'.format(MAX_REQUIRE_VERSION, current_verison))
else:
    print('pymycobot library version meets the requirements!')
    from pymycobot.mycobot import MyCobot


mc = None


def callback(data):
    global latest_data
    latest_data = [round(math.degrees(value), 2) for value in data.position]
    rospy.loginfo(f"Joint angles: {latest_data}")

def control_loop(event):
    if latest_data:
        rospy.loginfo(f"Sending angles: {latest_data}")
        mc.send_angles(latest_data, 25)

def listener():
    global mc
    rospy.init_node("control_slider", anonymous=True)

    rospy.Subscriber("joint_states", JointState, callback)
    port = rospy.get_param("~port", "/dev/ttyACM0")
    baud = rospy.get_param("~baud", 115200)
    print(port, baud)
    mc = MyCobot(port, baud)
    time.sleep(2) # open port,need wait

    # 启动定时器，每0.5秒执行一次控制循环
    rospy.Timer(rospy.Duration(0.5), control_loop)

    rospy.spin()



if __name__ == "__main__":
    listener()
