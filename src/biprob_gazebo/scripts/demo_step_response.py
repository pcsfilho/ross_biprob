#!/usr/bin/env python

import rospy
from biprob_gazebo.biprob import Biprob


if __name__=="__main__":
    rospy.init_node("biprob_simple_trajectory")
    
    rospy.loginfo("Instantiating biprob Client")
    biprob=Biprob()
    rospy.sleep(1) 
    rospy.loginfo("Iniciando demonstracao de Trajetoria ao Degrau") 

    rospy.loginfo("Movendo o joelho direito")
    print rospy.get_rostime().to_sec()    
    while rospy.get_rostime().to_sec() < 1.0:        
        biprob.set_angles({"j_knee_r":0.0})

        print rospy.get_rostime().to_sec()

    while rospy.get_rostime().to_sec() < 5.0:        
        biprob.set_angles({"j_knee_r":0.1})
        print rospy.get_rostime().to_sec()


    rospy.sleep(0.3)
        
    rospy.loginfo("Finalizando demonstracao de movimentos do Biprob")
