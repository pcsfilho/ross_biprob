#!/usr/bin/env python

import rospy
from biprob_gazebo.biprob import Biprob


if __name__=="__main__":
    rospy.init_node("walker_demo")
    
    rospy.loginfo("Instantiating biprob Client")
    biprob=Biprob()
    rospy.sleep(1) 
    rospy.loginfo("biprob Walker Demo Starting")
    rospy.loginfo("Moving left leg")
    biprob.set_angles({"j_thigh2_l":0.2})
    rospy.sleep(0.3)
    biprob.set_angles({"j_thigh2_l":0.4})
    rospy.sleep(0.3)
    biprob.set_angles({"j_thigh2_l":0.6})
    rospy.sleep(1.0)
    rospy.loginfo("Moving knee")
    biprob.set_angles({"j_tibia_l":-0.3})
    rospy.sleep(0.3)
    biprob.set_angles({"j_tibia_l":-0.6})
    rospy.sleep(0.3)
    biprob.set_angles({"j_tibia_l":-0.9})
    rospy.sleep(3.0)
    biprob.set_angles({"j_thigh2_l":0.0})    
    rospy.sleep(1.0)
    biprob.set_angles({"j_tibia_l":0.0})
    rospy.sleep(1.0)
    
    rospy.loginfo("biprob Walker Demo Finished")
