#Code to get a drone moving around using ROS actions as part of projects done via RoboIgniteAcademy
#! /usr/bin/env python

import rospy
import time
import actionlib
from ardrone_as.msg import ArdroneAction, ArdroneGoal, ArdroneResult, ArdroneFeedback
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty

# We create some constants with the corresponing vaules from the SimpleGoalState class
PENDING = 0
ACTIVE = 1
DONE = 2
WARN = 3
ERROR = 4

Image_Count = 1

# definition of the feedback callback. This will be called when feedback
# is received from the action server
# it just prints a message indicating a new message has been received
def feedback_callback(feedback):

    global Image_Count
    print('[Feedback] image n.%d received'%Image_Count)
    Image_Count += 1

# initializes the action client node
rospy.init_node('drone_action_client')

action_server_name = '/ardrone_action_server'
client = actionlib.SimpleActionClient(action_server_name, ArdroneAction)
move = rospy.Publisher('/cmd_vel', Twist, queue_size=1) #Create a Publisher to move the drone
move_msg = Twist() #Create the message to move the drone
takeoff = rospy.Publisher('/drone/takeoff', Empty, queue_size=1) #Create a Publisher to takeoff the drone
takeoff_msg = Empty() #Create the message to takeoff the drone
land = rospy.Publisher('/drone/land', Empty, queue_size=1) #Create a Publisher to land the drone
land_msg = Empty() #Create the message to land the drone

# waits until the action server is up and running
rospy.loginfo('Server wait time '+action_server_name)
client.wait_for_server()
rospy.loginfo('Found Server'+action_server_name)

# creates a goal to send to the action server
goal = ArdroneGoal()
goal.nseconds = 10 # indicates, take pictures along 10 seconds

client.send_goal(goal, feedback_cb=feedback_callback)


# You can access the SimpleAction Variable "simple_state", that will be 1 if active, and 2 when finished.
#Its a variable, better use a function like get_state.
#state = client.simple_state
# state_result will give the FINAL STATE. Will be 1 when Active, and 2 if NO ERROR, 3 If Any Warning, and 3 if ERROR
state_result = client.get_state()

rate = rospy.Rate(1)

rospy.loginfo("state_result: "+str(state_result))

#We takeoff the drone during the first 3 seconds
i=0
while not i == 3:
    takeoff.publish(takeoff_msg)
    rospy.loginfo('Flying up')
    time.sleep(1)
    i += 1

#We move the drone in a circle wile the state of the Action is not DONE yet
while state_result < DONE:
    move_msg.linear.x = 1
    move_msg.angular.z = 1
    move.publish(move_msg)
    rate.sleep()
    state_result = client.get_state()
    rospy.loginfo('Executing movements')
    rospy.loginfo("state_result: "+str(state_result))
    
rospy.loginfo("[Result] State: "+str(state_result))
if state_result == ERROR:
    rospy.logerr("Server error")
if state_result == WARN:
    rospy.logwarn("Server error")

# We land the drone when the action is finished
i=0
while not i == 3:
    move_msg.linear.x = 0
    move_msg.angular.z = 0
    move.publish(move_msg)
    land.publish(land_msg)
    rospy.loginfo('Finishing flight')
    time.sleep(1)
    i += 1
