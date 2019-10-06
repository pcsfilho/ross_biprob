#!/usr/bin/env python

import rospy
from biprob_gazebo.biprob import Biprob


if __name__=="__main__":
    rospy.init_node("walker_demo")    
    rospy.loginfo("Instanciando Clinte Biprob")
    biprob=Biprob()
    rospy.sleep(1) 
    rospy.loginfo("Iniciando demonstracao Biprob Walker")
    biprob.set_walk_velocity(0.2,0,0)
    rospy.sleep(10)    
    rospy.loginfo("stop")
    biprob.set_walk_velocity(0,0,0)    
    rospy.loginfo("finalizando demonstracao Biprob Walker")
