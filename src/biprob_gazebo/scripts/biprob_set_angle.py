#!/usr/bin/env python

import rospy
from biprob_gazebo.biprob import Biprob


if __name__=="__main__":
    rospy.init_node("biprob_simple_trajectory")
    
    rospy.loginfo("Instantiating biprob Client")
    biprob=Biprob()
    rospy.sleep(1) 
    rospy.loginfo("Iniciando demonstracao de movimentos do Biprob ")    
    rospy.loginfo("Movendo o joelho direito")
    biprob.set_angles({"j_knee_r":0.3})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.5})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.7})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.9})
    rospy.sleep(2.0)
    biprob.set_angles({"j_knee_r":0.7})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.5})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.3})
    rospy.sleep(0.3)
    biprob.set_angles({"j_knee_r":0.0})       
    rospy.sleep(1.0)    
    rospy.loginfo("Finalisando demonstracao de movimentos do Biprob")
